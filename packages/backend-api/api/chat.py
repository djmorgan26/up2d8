import uuid
import logging
from datetime import UTC, datetime

from google import genai
from google.genai import types
from dependencies import get_db_client, get_gemini_api_key
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

router = APIRouter(tags=["Chat"])
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    prompt: str


class SessionCreate(BaseModel):
    user_id: str
    title: str


class MessageContent(BaseModel):
    content: str


@router.post("/api/chat", status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest, api_key: str = Depends(get_gemini_api_key)):
    """
    Send a chat message to the AI assistant with Google Search grounding.
    The AI will search the web for current information when needed.
    """
    try:
        # Initialize the new google-genai client
        client = genai.Client(api_key=api_key)

        # Configure Google Search grounding tool
        config = types.GenerateContentConfig(
            system_instruction="You are an AI assistant for UP2D8, a personal news digest and information management platform. Your goal is to help users stay updated and manage their information effectively. Provide concise, relevant, and helpful responses. Focus on news, summaries, and information retrieval. Avoid conversational filler and keep responses professional and to the point.",
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )

        # Generate content with web search grounding
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=request.prompt,
            config=config
        )

        # Extract sources from grounding metadata
        sources = []

        # Debug: Log the response structure
        logger.info(f"Response type: {type(response)}")
        logger.info(f"Response attributes: {dir(response)}")
        if hasattr(response, 'grounding_metadata'):
            logger.info(f"Has grounding_metadata: {response.grounding_metadata}")
            if response.grounding_metadata:
                logger.info(f"Grounding metadata attributes: {dir(response.grounding_metadata)}")

        # Check if grounding_metadata exists in the response
        if hasattr(response, 'grounding_metadata') and response.grounding_metadata:
            # The new API structure uses grounding_supports instead of grounding_chunks
            if hasattr(response.grounding_metadata, 'grounding_supports'):
                for support in response.grounding_metadata.grounding_supports:
                    # Each support may contain grounding_chunk_indices and segment info
                    if hasattr(support, 'segment') and support.segment:
                        segment = support.segment
                        if hasattr(segment, 'text'):
                            # Also try to get the actual chunk info
                            if hasattr(response.grounding_metadata, 'grounding_chunks'):
                                for idx in support.grounding_chunk_indices if hasattr(support, 'grounding_chunk_indices') else []:
                                    if idx < len(response.grounding_metadata.grounding_chunks):
                                        chunk = response.grounding_metadata.grounding_chunks[idx]
                                        if hasattr(chunk, 'web') and chunk.web:
                                            sources.append({
                                                "web": {
                                                    "uri": chunk.web.uri,
                                                    "title": chunk.web.title if hasattr(chunk.web, 'title') else chunk.web.uri
                                                }
                                            })
            # Fallback: Try accessing grounding_chunks directly
            elif hasattr(response.grounding_metadata, 'grounding_chunks'):
                for chunk in response.grounding_metadata.grounding_chunks:
                    if hasattr(chunk, 'web') and chunk.web:
                        sources.append({
                            "web": {
                                "uri": chunk.web.uri,
                                "title": chunk.web.title if hasattr(chunk.web, 'title') else chunk.web.uri
                            }
                        })

        return {"text": response.text, "sources": sources}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Gemini API error: {e}"
        )


@router.post("/api/sessions", status_code=status.HTTP_200_OK)
async def create_session(session_data: SessionCreate, db=Depends(get_db_client)):
    sessions_collection = db.sessions
    session_id = str(uuid.uuid4())
    new_session = {
        "session_id": session_id,
        "user_id": session_data.user_id,
        "title": session_data.title,
        "created_at": datetime.now(UTC),
        "messages": [],
    }
    sessions_collection.insert_one(new_session)
    return {"session_id": session_id}


@router.get("/api/users/{user_id}/sessions", status_code=status.HTTP_200_OK)
async def get_sessions(user_id: str, db=Depends(get_db_client)):
    sessions_collection = db.sessions
    sessions = list(sessions_collection.find({"user_id": user_id}, {"_id": 0}))
    return sessions


@router.post("/api/sessions/{session_id}/messages", status_code=status.HTTP_200_OK)
async def send_message(session_id: str, message_content: MessageContent, db=Depends(get_db_client)):
    sessions_collection = db.sessions
    result = sessions_collection.update_one(
        {"session_id": session_id},
        {
            "$push": {
                "messages": {
                    "role": "user",
                    "content": message_content.content,
                    "timestamp": datetime.now(UTC),
                }
            }
        },
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    return {"message": "Message sent."}


@router.get("/api/sessions/{session_id}/messages", status_code=status.HTTP_200_OK)
async def get_messages(session_id: str, db=Depends(get_db_client)):
    sessions_collection = db.sessions
    session = sessions_collection.find_one({"session_id": session_id}, {"_id": 0, "messages": 1})
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    return session.get("messages", [])
