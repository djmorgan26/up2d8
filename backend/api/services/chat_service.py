"""
Chat Service with RAG Integration for UP2D8

Provides conversational AI powered by LLMs with retrieval-augmented generation.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import structlog

from api.services.rag_service import get_rag_service, RAGContext
from api.services.llm_provider import get_llm_client
from api.db.session import SessionLocal
from api.db.models import ChatSession, ChatMessage, User

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
    ) -> ChatSession:
        """
        Create a new chat session.

        Args:
            user_id: ID of the user
            title: Optional title for the session

        Returns:
            ChatSession object
        """
        db = SessionLocal()
        try:
            session = ChatSession(
                user_id=user_id,
                title=title or "New Chat",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(session)
            db.commit()
            db.refresh(session)

            logger.info(
                "Created chat session",
                session_id=session.id,
                user_id=user_id,
            )

            return session

        finally:
            db.close()

    async def get_session(
        self,
        session_id: str,
        user_id: str,
    ) -> Optional[ChatSession]:
        """
        Get a chat session by ID.

        Args:
            session_id: ID of the session
            user_id: ID of the user (for authorization)

        Returns:
            ChatSession object or None
        """
        db = SessionLocal()
        try:
            session = (
                db.query(ChatSession)
                .filter(
                    ChatSession.id == session_id,
                    ChatSession.user_id == user_id,
                )
                .first()
            )

            return session

        finally:
            db.close()

    async def get_user_sessions(
        self,
        user_id: str,
        limit: int = 20,
    ) -> List[ChatSession]:
        """
        Get all chat sessions for a user.

        Args:
            user_id: ID of the user
            limit: Maximum number of sessions to return

        Returns:
            List of ChatSession objects
        """
        db = SessionLocal()
        try:
            sessions = (
                db.query(ChatSession)
                .filter(ChatSession.user_id == user_id)
                .order_by(ChatSession.updated_at.desc())
                .limit(limit)
                .all()
            )

            return sessions

        finally:
            db.close()

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
                "user_message": ChatMessage,
                "assistant_message": ChatMessage,
                "context": RAGContext (if use_rag=True),
                "session": ChatSession
            }
        """
        db = SessionLocal()
        try:
            # Get session
            session = (
                db.query(ChatSession)
                .filter(
                    ChatSession.id == session_id,
                    ChatSession.user_id == user_id,
                )
                .first()
            )

            if not session:
                raise ValueError(f"Session not found or unauthorized: {session_id}")

            # Store user message
            user_message = ChatMessage(
                session_id=session_id,
                role="user",
                content=message,
                created_at=datetime.utcnow(),
            )
            db.add(user_message)
            db.commit()
            db.refresh(user_message)

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
                    articles_found=len(context.articles),
                )

            # Build conversation history
            conversation_history = (
                db.query(ChatMessage)
                .filter(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.asc())
                .all()
            )

            # Generate AI response
            assistant_response = await self._generate_response(
                message=message,
                context=context,
                conversation_history=conversation_history[:-1],  # Exclude the message we just added
            )

            # Store assistant message
            assistant_message = ChatMessage(
                session_id=session_id,
                role="assistant",
                content=assistant_response,
                created_at=datetime.utcnow(),
                metadata={
                    "articles_used": [a.id for a in context.articles] if context else [],
                    "top_k": top_k,
                },
            )
            db.add(assistant_message)

            # Update session
            session.updated_at = datetime.utcnow()
            session.message_count = len(conversation_history) + 1

            # Auto-generate title for first message
            if session.message_count == 2 and session.title == "New Chat":
                session.title = message[:50] + ("..." if len(message) > 50 else "")

            db.commit()
            db.refresh(assistant_message)
            db.refresh(session)

            logger.info(
                "Assistant response generated",
                session_id=session_id,
                response_length=len(assistant_response),
                articles_used=len(context.articles) if context else 0,
            )

            return {
                "user_message": user_message,
                "assistant_message": assistant_message,
                "context": context,
                "session": session,
            }

        finally:
            db.close()

    async def _generate_response(
        self,
        message: str,
        context: Optional[RAGContext] = None,
        conversation_history: Optional[List[ChatMessage]] = None,
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
        if context and context.articles:
            context_text = context.format_for_llm()
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
                    "role": msg.role,
                    "content": msg.content,
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
        db = SessionLocal()
        try:
            session = (
                db.query(ChatSession)
                .filter(
                    ChatSession.id == session_id,
                    ChatSession.user_id == user_id,
                )
                .first()
            )

            if not session:
                return False

            # Delete all messages first
            db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()

            # Delete session
            db.delete(session)
            db.commit()

            logger.info(
                "Chat session deleted",
                session_id=session_id,
                user_id=user_id,
            )

            return True

        finally:
            db.close()

    async def get_messages(
        self,
        session_id: str,
        user_id: str,
        limit: int = 100,
    ) -> List[ChatMessage]:
        """
        Get messages from a chat session.

        Args:
            session_id: ID of the session
            user_id: ID of the user (for authorization)
            limit: Maximum number of messages to return

        Returns:
            List of ChatMessage objects
        """
        db = SessionLocal()
        try:
            # Verify session ownership
            session = (
                db.query(ChatSession)
                .filter(
                    ChatSession.id == session_id,
                    ChatSession.user_id == user_id,
                )
                .first()
            )

            if not session:
                raise ValueError(f"Session not found or unauthorized: {session_id}")

            # Get messages
            messages = (
                db.query(ChatMessage)
                .filter(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.asc())
                .limit(limit)
                .all()
            )

            return messages

        finally:
            db.close()


# Singleton instance
_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """Get or create the global chat service instance"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
