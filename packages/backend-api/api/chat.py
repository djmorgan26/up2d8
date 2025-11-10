import uuid
import logging
from datetime import UTC, datetime

from google import genai
from google.genai import types
from dependencies import get_db_client, get_gemini_api_key
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from shared.retry_utils import retry_with_backoff

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

        # System instruction for UP2D8 assistant
        system_instruction = """
        You are UP2D8, an AI assistant for a personal news digest and information management platform.

        Your role:
        - Help users stay updated with accurate, recent information using Google Search grounding.
        - Summarize clearly and concisely.
        - Maintain a professional, helpful, and neutral tone.
        - Always cite grounded sources when applicable.
        - Avoid speculation or filler.

        Response format:
        - Start with a concise answer or summary.
        - Include "Sources:" if grounded data is referenced.
        """

        # Configure Google Search grounding tool
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )

        # Generate content with web search grounding (with retry logic for transient failures)
        @retry_with_backoff(max_attempts=3, base_delay=2.0, max_delay=30.0)
        def _generate_with_retry():
            return client.models.generate_content(
                model="gemini-2.5-flash",
                contents=request.prompt,
                config=config
            )

        response = _generate_with_retry()

        # Extract sources from grounding metadata
        sources = []

        # Debug: Log the full response object as dict
        try:
            import json
            response_dict = response.to_dict() if hasattr(response, 'to_dict') else {}
            logger.info(f"Full response dict: {json.dumps(response_dict, indent=2, default=str)}")
        except Exception as e:
            logger.warning(f"Could not serialize response: {e}")
            logger.info(f"Response type: {type(response)}")
            logger.info(f"Response str: {str(response)}")

        # Extract grounding metadata from first candidate (standard structure)
        try:
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]

                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    metadata = candidate.grounding_metadata
                    logger.info(f"✓ Found grounding_metadata")

                    # Extract sources from grounding_chunks (the main source list)
                    if hasattr(metadata, 'grounding_chunks') and metadata.grounding_chunks:
                        logger.info(f"✓ Found {len(metadata.grounding_chunks)} grounding chunks")

                        for chunk in metadata.grounding_chunks:
                            if hasattr(chunk, 'web') and chunk.web:
                                web_source = {
                                    "uri": chunk.web.uri,
                                    "title": getattr(chunk.web, 'title', chunk.web.uri)
                                }
                                sources.append({"web": web_source})
                                logger.info(f"  - Added source: {web_source['title']}")
                    else:
                        logger.info("✗ No grounding_chunks found")

                    # Also log search entry point if available
                    if hasattr(metadata, 'search_entry_point') and metadata.search_entry_point:
                        logger.info(f"✓ Search entry point available")
                else:
                    logger.info("✗ No grounding_metadata in candidate")
            else:
                logger.info("✗ No candidates in response")
        except Exception as e:
            logger.error(f"Error extracting sources: {e}", exc_info=True)

        logger.info(f"Final sources count: {len(sources)}")

        return {
            "status": "success",
            "model": "gemini-2.5-flash",
            "reply": response.text.strip(),
            "sources": sources
        }
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
