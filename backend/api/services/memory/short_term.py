"""
Layer 2: Short-Term Memory

Maintains conversation history for the current chat session.
Enables context-aware responses and follow-up questions.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pymongo.database import Database
import structlog

from api.db.session import get_db
from api.db.cosmos_db import CosmosCollections

logger = structlog.get_logger()


class ShortTermMemory:
    """
    Layer 2 Memory: Conversation History

    Provides:
    - Current session's message history
    - Recent conversation context
    - Message tracking and retrieval

    Priority: HIGH (enables context-aware responses)

    TODO: Implement MongoDB queries. For now, this is stubbed to unblock API startup.
    """

    def __init__(self, session_id: str, user_id: str, db: Database):
        """
        Initialize short-term memory

        Args:
            session_id: Chat session ID
            user_id: User ID
            db: Database session
        """
        self.session_id = session_id
        self.user_id = user_id
        self.db = db
        self._message_cache: List[Dict[str, Any]] = []
        self._cache_valid = False

        logger.info("short_term_memory_initialized", session_id=session_id, user_id=user_id)

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add a message to conversation history

        Args:
            role: Message role ("user" or "assistant")
            content: Message content
            metadata: Optional metadata (sources, citations, etc.)

        Returns:
            Message dictionary
        """
        message = {
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Add to cache
        self._message_cache.append(message)

        logger.info(
            "message_added_to_memory",
            session_id=self.session_id,
            role=role,
            content_length=len(content)
        )

        return message

    def get_messages(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get conversation messages

        Args:
            limit: Maximum number of messages to return (None = all)

        Returns:
            List of message dictionaries
        """
        # Load from database if cache invalid
        if not self._cache_valid:
            self._load_from_db()

        # Return limited or all messages
        if limit:
            return self._message_cache[-limit:]
        return self._message_cache.copy()

    def get_recent_context(self, num_turns: int = 5) -> str:
        """
        Get recent conversation context as formatted text

        Args:
            num_turns: Number of conversation turns to include

        Returns:
            Formatted conversation history
        """
        messages = self.get_messages(limit=num_turns * 2)  # *2 for user+assistant pairs

        context_parts = []
        for msg in messages:
            role_prefix = "User" if msg["role"] == "user" else "Assistant"
            context_parts.append(f"{role_prefix}: {msg['content']}")

        return "\n".join(context_parts)

    def get_langchain_messages(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get messages in LangChain format

        Args:
            limit: Maximum number of messages

        Returns:
            List of LangChain-compatible message dicts
        """
        messages = self.get_messages(limit=limit)

        return [
            {
                "role": msg["role"],
                "content": msg["content"]
            }
            for msg in messages
        ]

    def search_messages(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search messages by keyword

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            Matching messages
        """
        messages = self.get_messages()
        query_lower = query.lower()

        matching = [
            msg for msg in messages
            if query_lower in msg['content'].lower()
        ]

        return matching[:limit]

    def clear(self):
        """Clear short-term memory cache"""
        self._message_cache.clear()
        self._cache_valid = False

        logger.info("short_term_memory_cleared", session_id=self.session_id)

    def get_summary(self) -> str:
        """
        Get a summary of the conversation

        Returns:
            Summary text
        """
        messages = self.get_messages()

        if not messages:
            return "No conversation history yet."

        user_messages = [m for m in messages if m["role"] == "user"]
        assistant_messages = [m for m in messages if m["role"] == "assistant"]

        return (
            f"Conversation with {len(messages)} messages total:\n"
            f"- {len(user_messages)} user messages\n"
            f"- {len(assistant_messages)} assistant responses\n"
            f"Started: {messages[0]['timestamp'][:19]}"
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        messages = self.get_messages()
        return {
            "layer": "short_term",
            "session_id": self.session_id,
            "user_id": self.user_id,
            "message_count": len(messages),
            "user_message_count": len([m for m in messages if m["role"] == "user"]),
            "assistant_message_count": len([m for m in messages if m["role"] == "assistant"]),
            "cache_valid": self._cache_valid,
        }

    def _load_from_db(self):
        """
        Load messages from database
        """
        # Load chat messages for this session from MongoDB
        messages = list(
            self.db[CosmosCollections.CHAT_MESSAGES]
            .find({
                "session_id": self.session_id,
                "user_id": self.user_id
            })
            .sort("timestamp", 1)  # Chronological order
        )

        # Convert to memory format
        self._message_cache = [
            {
                "role": msg.get("role"),
                "content": msg.get("content"),
                "metadata": msg.get("metadata", {}),
                "timestamp": msg.get("timestamp").isoformat() if msg.get("timestamp") else datetime.utcnow().isoformat()
            }
            for msg in messages
        ]

        self._cache_valid = True

        logger.info(
            "short_term_memory_loaded_from_db",
            session_id=self.session_id,
            message_count=len(self._message_cache)
        )


# Helper function for easy access
def get_short_term_memory(session_id: str, user_id: str, db: Database) -> ShortTermMemory:
    """
    Get short-term memory for a chat session

    Args:
        session_id: Chat session ID
        user_id: User ID
        db: Database session

    Returns:
        ShortTermMemory instance
    """
    return ShortTermMemory(session_id=session_id, user_id=user_id, db=db)
