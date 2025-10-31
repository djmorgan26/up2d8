"""
Chat Service with RAG Integration for UP2D8

Provides conversational AI powered by LLMs with retrieval-augmented generation.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import structlog
import uuid

from api.services.rag_service import get_rag_service, RAGContext
from api.services.llm_provider import get_llm_client
from api.db.session import get_db
from api.db.cosmos_db import CosmosCollections
from api.db.models import ChatSessionDocument, ChatMessageDocument

logger = structlog.get_logger()


class ChatService:
    """Service for managing chat conversations with RAG"""

    def __init__(self):
        self.rag_service = get_rag_service()
        self.llm_client = get_llm_client()

    async def create_session(
        self,
        user_id: str,
        title: Optional[str] = None,
        context_type: Optional[str] = None,
        context_id: Optional[str] = None,
    ) -> dict:
        """
        Create a new chat session.

        Args:
            user_id: ID of the user
            title: Optional title for the session
            context_type: Type of context (e.g., "digest", "article")
            context_id: ID of the context object

        Returns:
            Chat session document
        """
        db = get_db()

        session = ChatSessionDocument.create(
            user_id=user_id,
            context_type=context_type,
            context_id=context_id,
        )

        db[CosmosCollections.CHAT_SESSIONS].insert_one(session)

        logger.info(
            "Created chat session",
            session_id=session["id"],
            user_id=user_id,
        )

        return session

    async def get_session(
        self,
        session_id: str,
        user_id: str,
    ) -> Optional[dict]:
        """
        Get a chat session by ID.

        Args:
            session_id: ID of the session
            user_id: ID of the user (for authorization)

        Returns:
            Chat session document or None
        """
        db = get_db()

        session = db[CosmosCollections.CHAT_SESSIONS].find_one({
            "id": session_id,
            "user_id": user_id,
        })

        return session

    async def get_user_sessions(
        self,
        user_id: str,
        limit: int = 20,
    ) -> List[dict]:
        """
        Get all chat sessions for a user.

        Args:
            user_id: ID of the user
            limit: Maximum number of sessions to return

        Returns:
            List of chat session documents
        """
        db = get_db()

        sessions = list(
            db[CosmosCollections.CHAT_SESSIONS]
            .find({"user_id": user_id})
            .sort("last_message_at", -1)
            .limit(limit)
        )

        return sessions

    async def send_message(
        self,
        session_id: str,
        user_id: str,
        message: str,
        use_rag: bool = True,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        Send a message in a chat session and get AI response.

        Args:
            session_id: ID of the chat session
            user_id: ID of the user
            message: User's message
            use_rag: Whether to use RAG for context retrieval
            top_k: Number of articles to retrieve for context

        Returns:
            {
                "user_message": dict,
                "assistant_message": dict,
                "context": RAGContext (if use_rag=True),
                "session": dict
            }
        """
        db = get_db()

        # Get session
        session = db[CosmosCollections.CHAT_SESSIONS].find_one({
            "id": session_id,
            "user_id": user_id,
        })

        if not session:
            raise ValueError(f"Session not found or unauthorized: {session_id}")

        # Store user message
        user_message = ChatMessageDocument.create(
            session_id=session_id,
            role="user",
            content=message,
        )
        db[CosmosCollections.CHAT_MESSAGES].insert_one(user_message)

        logger.info(
            "User message stored",
            session_id=session_id,
            message_length=len(message),
        )

        # Retrieve context if RAG is enabled
        context = None
        if use_rag:
            context = await self.rag_service.search_user_articles(
                query=message,
                user_id=user_id,
                top_k=top_k,
            )

            logger.info(
                "Context retrieved",
                session_id=session_id,
                articles_found=len(context.articles) if context else 0,
            )

        # Build conversation history
        conversation_history = list(
            db[CosmosCollections.CHAT_MESSAGES]
            .find({"session_id": session_id})
            .sort("created_at", 1)
        )

        # Generate AI response
        assistant_response = await self._generate_response(
            message=message,
            context=context,
            conversation_history=conversation_history[:-1],  # Exclude the message we just added
        )

        # Store assistant message
        assistant_message = ChatMessageDocument.create(
            session_id=session_id,
            role="assistant",
            content=assistant_response,
            retrieved_articles=[
                a["id"] for a in context.articles
            ] if context and hasattr(context, "articles") else [],
        )
        db[CosmosCollections.CHAT_MESSAGES].insert_one(assistant_message)

        # Update session
        message_count = len(conversation_history) + 1
        db[CosmosCollections.CHAT_SESSIONS].update_one(
            {"id": session_id},
            {
                "$set": {
                    "last_message_at": datetime.utcnow(),
                    "message_count": message_count,
                }
            }
        )

        # Refresh session
        session = db[CosmosCollections.CHAT_SESSIONS].find_one({"id": session_id})

        logger.info(
            "Assistant response generated",
            session_id=session_id,
            response_length=len(assistant_response),
            articles_used=len(context.articles) if context and hasattr(context, "articles") else 0,
        )

        return {
            "user_message": user_message,
            "assistant_message": assistant_message,
            "context": context,
            "session": session,
        }

    async def _generate_response(
        self,
        message: str,
        context: Optional[RAGContext] = None,
        conversation_history: Optional[List[dict]] = None,
    ) -> str:
        """
        Generate AI response using LLM with RAG context.

        Args:
            message: Current user message
            context: Retrieved context from RAG
            conversation_history: Previous messages in the conversation

        Returns:
            AI-generated response
        """
        # Build system prompt
        system_prompt = """You are UP2D8 AI, an intelligent assistant that helps users understand and explore industry news and developments.

Your capabilities:
- Answer questions about recent articles and industry trends
- Provide summaries and insights from retrieved articles
- Help users discover connections between different news items
- Explain technical concepts in accessible language

Guidelines:
- Be concise and informative
- Cite specific articles when referencing information (use [1], [2], etc.)
- If you don't have enough context to answer accurately, say so
- Focus on the user's question and be helpful"""

        # Build user prompt with context
        if context and hasattr(context, "articles") and context.articles:
            context_text = context.format_for_llm() if hasattr(context, "format_for_llm") else str(context)
            user_prompt = f"""Based on the following articles:

{context_text}

User question: {message}

Please provide a helpful answer, citing specific articles using [1], [2], etc. when referencing information."""
        else:
            user_prompt = message

        # Add conversation history
        messages = []
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                messages.append({
                    "role": msg.get("role"),
                    "content": msg.get("content"),
                })

        # Add current message
        messages.append({
            "role": "user",
            "content": user_prompt,
        })

        # Generate response
        try:
            response = await self.llm_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                conversation_history=messages[:-1] if messages[:-1] else None,
                max_tokens=1000,
                temperature=0.7,
            )

            return response

        except Exception as e:
            logger.error("Error generating LLM response", error=str(e), exc_info=True)
            return "I apologize, but I'm having trouble generating a response right now. Please try again in a moment."

    async def delete_session(
        self,
        session_id: str,
        user_id: str,
    ) -> bool:
        """
        Delete a chat session.

        Args:
            session_id: ID of the session
            user_id: ID of the user (for authorization)

        Returns:
            True if deleted, False if not found
        """
        db = get_db()

        session = db[CosmosCollections.CHAT_SESSIONS].find_one({
            "id": session_id,
            "user_id": user_id,
        })

        if not session:
            return False

        # Delete all messages first
        db[CosmosCollections.CHAT_MESSAGES].delete_many({"session_id": session_id})

        # Delete session
        db[CosmosCollections.CHAT_SESSIONS].delete_one({"id": session_id})

        logger.info(
            "Chat session deleted",
            session_id=session_id,
            user_id=user_id,
        )

        return True

    async def get_messages(
        self,
        session_id: str,
        user_id: str,
        limit: int = 100,
    ) -> List[dict]:
        """
        Get messages from a chat session.

        Args:
            session_id: ID of the session
            user_id: ID of the user (for authorization)
            limit: Maximum number of messages to return

        Returns:
            List of chat message documents
        """
        db = get_db()

        # Verify session ownership
        session = db[CosmosCollections.CHAT_SESSIONS].find_one({
            "id": session_id,
            "user_id": user_id,
        })

        if not session:
            raise ValueError(f"Session not found or unauthorized: {session_id}")

        # Get messages
        messages = list(
            db[CosmosCollections.CHAT_MESSAGES]
            .find({"session_id": session_id})
            .sort("created_at", 1)
            .limit(limit)
        )

        return messages


# Singleton instance
_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """Get or create the global chat service instance"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
