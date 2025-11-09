import uuid
from datetime import UTC, datetime

import google.generativeai as genai
from dependencies import get_db_client, get_gemini_api_key
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

router = APIRouter(tags=["Chat"])


class ChatRequest(BaseModel):
    prompt: str


class SessionCreate(BaseModel):
    user_id: str
    title: str


class MessageContent(BaseModel):
    content: str


@router.post("/api/chat", status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest, api_key: str = Depends(get_gemini_api_key)):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction="You are an AI assistant for UP2D8, a personal news digest and information management platform. Your goal is to help users stay updated and manage their information effectively. Provide concise, relevant, and helpful responses. Focus on news, summaries, and information retrieval. Avoid conversational filler and keep responses professional and to the point.",
        )
        response = model.generate_content(request.prompt)
        return {"text": response.text, "sources": []}
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
