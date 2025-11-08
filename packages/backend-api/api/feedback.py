from fastapi import APIRouter, status, Depends
from pydantic import BaseModel
from datetime import datetime, UTC
from dependencies import get_db_client # Import the new dependency

router = APIRouter()

class FeedbackCreate(BaseModel):
    message_id: str
    user_id: str
    rating: str

@router.post("/api/feedback", status_code=status.HTTP_201_CREATED)
async def create_feedback(feedback: FeedbackCreate, db=Depends(get_db_client)):
    feedback_collection = db.feedback
    feedback_entry = {
        "message_id": feedback.message_id,
        "user_id": feedback.user_id,
        "rating": feedback.rating,
        "timestamp": datetime.now(UTC)
    }
    feedback_collection.insert_one(feedback_entry)
    return {"message": "Feedback received."}
