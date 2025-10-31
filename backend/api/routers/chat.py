"""API endpoints for chat functionality with RAG."""

from typing import List, Optional
import json
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from api.utils.auth import get_current_user
# User is dict type from get_current_user
from api.services.chat_service import get_chat_service
from api.services.rag_service import get_rag_service
from api.services.agent import get_conversational_agent
from api.db.session import get_database
from api.db.cosmos_db import CosmosCollections

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


# ============================================================================
# Request/Response Models
# ============================================================================


class CreateSessionRequest(BaseModel):
    """Request to create a new chat session"""

    title: Optional[str] = Field(None, description="Optional title for the session")


class SendMessageRequest(BaseModel):
    """Request to send a message in a chat session"""

    message: str = Field(..., min_length=1, max_length=5000, description="User's message")
    use_rag: bool = Field(True, description="Whether to use RAG for context retrieval")
    top_k: int = Field(5, ge=1, le=20, description="Number of articles to retrieve")


class SessionResponse(BaseModel):
    """Response model for chat session"""

    id: str
    user_id: str
    title: str
    message_count: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Response model for chat message"""

    id: str
    session_id: str
    role: str
    content: str
    created_at: str
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class ArticleContextResponse(BaseModel):
    """Response model for article context"""

    id: str
    title: str
    summary: Optional[str]
    source_url: str
    published_at: Optional[str]
    companies: List[str]
    industries: List[str]
    relevance_score: float


class SendMessageResponse(BaseModel):
    """Response for send message endpoint"""

    user_message: MessageResponse
    assistant_message: MessageResponse
    context: Optional[List[ArticleContextResponse]] = None
    session: SessionResponse


class SearchArticlesRequest(BaseModel):
    """Request to search articles semantically"""

    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(10, ge=1, le=50)
    companies: Optional[List[str]] = None
    industries: Optional[List[str]] = None


# ============================================================================
# Session Management Endpoints
# ============================================================================


@router.post("/sessions", response_model=SessionResponse)
async def create_chat_session(
    request: CreateSessionRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new chat session.

    Requires authentication.
    """
    chat_service = get_chat_service()

    session = await chat_service.create_session(
        user_id=current_user.id,
        title=request.title,
    )

    return SessionResponse(
        id=session.id,
        user_id=session.user_id,
        title=session.title,
        message_count=session.message_count,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
    )


@router.get("/sessions", response_model=List[SessionResponse])
async def list_chat_sessions(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of sessions to return"),
    current_user: dict = Depends(get_current_user),
):
    """
    List all chat sessions for the current user.

    Requires authentication.
    """
    chat_service = get_chat_service()

    sessions = await chat_service.get_user_sessions(
        user_id=current_user.id,
        limit=limit,
    )

    return [
        SessionResponse(
            id=session.id,
            user_id=session.user_id,
            title=session.title,
            message_count=session.message_count,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat(),
        )
        for session in sessions
    ]


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_chat_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Get a specific chat session.

    Requires authentication.
    """
    chat_service = get_chat_service()

    session = await chat_service.get_session(
        session_id=session_id,
        user_id=current_user.id,
    )

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse(
        id=session.id,
        user_id=session.user_id,
        title=session.title,
        message_count=session.message_count,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
    )


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Delete a chat session.

    Requires authentication.
    """
    chat_service = get_chat_service()

    deleted = await chat_service.delete_session(
        session_id=session_id,
        user_id=current_user.id,
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"success": True, "message": "Session deleted"}


# ============================================================================
# Message Endpoints
# ============================================================================


@router.post("/sessions/{session_id}/messages", response_model=SendMessageResponse)
async def send_chat_message(
    session_id: str,
    request: SendMessageRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Send a message in a chat session and get AI response with RAG context.

    Requires authentication.
    """
    chat_service = get_chat_service()

    try:
        result = await chat_service.send_message(
            session_id=session_id,
            user_id=current_user.id,
            message=request.message,
            use_rag=request.use_rag,
            top_k=request.top_k,
        )

        # Format context for response
        context_articles = None
        if result["context"] and result["context"].articles:
            context_articles = [
                ArticleContextResponse(
                    id=article.id,
                    title=article.title,
                    summary=article.summary_standard,
                    source_url=article.source_url,
                    published_at=article.published_at.isoformat() if article.published_at else None,
                    companies=article.companies or [],
                    industries=article.industries or [],
                    relevance_score=score,
                )
                for article, score in zip(
                    result["context"].articles,
                    result["context"].relevance_scores,
                )
            ]

        return SendMessageResponse(
            user_message=MessageResponse(
                id=result["user_message"].id,
                session_id=result["user_message"].session_id,
                role=result["user_message"].role,
                content=result["user_message"].content,
                created_at=result["user_message"].created_at.isoformat(),
                metadata=result["user_message"].metadata,
            ),
            assistant_message=MessageResponse(
                id=result["assistant_message"].id,
                session_id=result["assistant_message"].session_id,
                role=result["assistant_message"].role,
                content=result["assistant_message"].content,
                created_at=result["assistant_message"].created_at.isoformat(),
                metadata=result["assistant_message"].metadata,
            ),
            context=context_articles,
            session=SessionResponse(
                id=result["session"].id,
                user_id=result["session"].user_id,
                title=result["session"].title,
                message_count=result["session"].message_count,
                created_at=result["session"].created_at.isoformat(),
                updated_at=result["session"].updated_at.isoformat(),
            ),
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_chat_messages(
    session_id: str,
    limit: int = Query(100, ge=1, le=500, description="Maximum number of messages to return"),
    current_user: dict = Depends(get_current_user),
):
    """
    Get messages from a chat session.

    Requires authentication.
    """
    chat_service = get_chat_service()

    try:
        messages = await chat_service.get_messages(
            session_id=session_id,
            user_id=current_user.id,
            limit=limit,
        )

        return [
            MessageResponse(
                id=msg.id,
                session_id=msg.session_id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at.isoformat(),
                metadata=msg.metadata,
            )
            for msg in messages
        ]

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# Search Endpoints
# ============================================================================


@router.post("/search", response_model=List[ArticleContextResponse])
async def search_articles(
    request: SearchArticlesRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Semantic search for articles using RAG.

    Requires authentication.
    Returns articles relevant to the query.
    """
    rag_service = get_rag_service()

    context = await rag_service.search_user_articles(
        query=request.query,
        user_id=current_user.id,
        top_k=request.top_k,
    )

    return [
        ArticleContextResponse(
            id=article.id,
            title=article.title,
            summary=article.summary_standard,
            source_url=article.source_url,
            published_at=article.published_at.isoformat() if article.published_at else None,
            companies=article.companies or [],
            industries=article.industries or [],
            relevance_score=score,
        )
        for article, score in zip(context.articles, context.relevance_scores)
    ]


@router.get("/articles/{article_id}/similar", response_model=List[ArticleContextResponse])
async def get_similar_articles(
    article_id: str,
    top_k: int = Query(5, ge=1, le=20, description="Number of similar articles to return"),
    current_user: dict = Depends(get_current_user),
):
    """
    Find articles similar to a given article.

    Requires authentication.
    """
    rag_service = get_rag_service()

    try:
        context = await rag_service.get_similar_articles(
            article_id=article_id,
            top_k=top_k,
        )

        return [
            ArticleContextResponse(
                id=article.id,
                title=article.title,
                summary=article.summary_standard,
                source_url=article.source_url,
                published_at=article.published_at.isoformat() if article.published_at else None,
                companies=article.companies or [],
                industries=article.industries or [],
                relevance_score=score,
            )
            for article, score in zip(context.articles, context.relevance_scores)
        ]

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# Health Check
# ============================================================================


@router.get("/health")
async def chat_health():
    """
    Health check for chat system.

    No authentication required.
    """
    # Test that services can be initialized
    try:
        chat_service = get_chat_service()
        rag_service = get_rag_service()

        return {
            "status": "healthy",
            "chat_service": "initialized",
            "rag_service": "initialized",
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }


# ============================================================================
# WebSocket Chat with LangGraph Agent
# ============================================================================


@router.websocket("/ws/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(..., description="JWT access token for authentication"),
):
    """
    WebSocket endpoint for real-time chat with conversational AI agent.

    Uses LangGraph agent with 3-layer memory system for intelligent responses.

    Protocol:
    1. Client connects with JWT token as query parameter
    2. Client sends JSON messages: {"message": "user message text"}
    3. Server sends streaming JSON chunks:
       - {"type": "start", "data": {...}}
       - {"type": "chunk", "data": {"content": "..."}}
       - {"type": "source", "data": {"title": "...", "relevance": 0.9}}
       - {"type": "end", "data": {"confidence": 0.85, "memory_layers": [...]}}
       - {"type": "error", "data": {"message": "..."}}

    Example:
    ws://localhost:8000/api/v1/chat/ws/session-id?token=your_jwt_token
    """
    await websocket.accept()

    db = None
    agent = None

    try:
        # Verify token and get user
        from api.utils.auth import decode_token

        try:
            payload = decode_token(token)
            user_id = payload.get("sub")

            if not user_id:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "Invalid token"}
                })
                await websocket.close(code=1008, reason="Invalid token")
                return

        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "data": {"message": f"Authentication failed: {str(e)}"}
            })
            await websocket.close(code=1008, reason="Authentication failed")
            return

        # Initialize database session
        db = get_database()

        # Verify user exists
        user = db[CosmosCollections.USERS].find_one({"id": user_id})
        if not user:
            await websocket.send_json({
                "type": "error",
                "data": {"message": "User not found"}
            })
            await websocket.close(code=1008, reason="User not found")
            return

        # Initialize conversational agent with Groq for better responses
        agent = get_conversational_agent(
            user_id=str(user_id),
            session_id=session_id,
            db=db,
            use_groq=True
        )

        # Send ready message
        await websocket.send_json({
            "type": "ready",
            "data": {
                "session_id": session_id,
                "user_id": str(user_id)
            }
        })

        # Handle messages
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            if not data.get("message"):
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "Message field is required"}
                })
                continue

            user_message = data["message"]

            # Send start event
            await websocket.send_json({
                "type": "start",
                "data": {
                    "user_message": user_message,
                    "timestamp": agent.short_term_memory.get_messages()[-1]["timestamp"] if agent.short_term_memory.get_messages() else None
                }
            })

            try:
                # Process message through agent
                response = await agent.chat(user_message)

                # Stream response in chunks (simulate streaming for now)
                response_text = response["response"]
                chunk_size = 50  # Characters per chunk

                for i in range(0, len(response_text), chunk_size):
                    chunk = response_text[i:i + chunk_size]
                    await websocket.send_json({
                        "type": "chunk",
                        "data": {"content": chunk}
                    })

                # Send sources
                if response.get("sources"):
                    for source in response["sources"]:
                        await websocket.send_json({
                            "type": "source",
                            "data": {
                                "id": source["id"],
                                "title": source["title"],
                                "url": source.get("url"),
                                "relevance_score": source["relevance_score"]
                            }
                        })

                # Send completion event
                await websocket.send_json({
                    "type": "end",
                    "data": {
                        "confidence": response.get("confidence"),
                        "memory_layers_used": response.get("memory_layers_used"),
                        "query_type": response.get("query_type"),
                        "full_response": response_text
                    }
                })

            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": f"Error processing message: {str(e)}"}
                })

    except WebSocketDisconnect:
        # Client disconnected normally
        pass

    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "data": {"message": f"Server error: {str(e)}"}
            })
        except:
            pass

    finally:
        # Clean up
        if db:
            db.close()

        try:
            await websocket.close()
        except:
            pass
