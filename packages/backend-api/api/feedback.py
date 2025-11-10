from datetime import UTC, datetime

from dependencies import get_db_client  # Import the new dependency
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from shared.validation import UUIDField, FeedbackRatingField

router = APIRouter(tags=["Feedback"])


class FeedbackCreate(BaseModel):
    """Request model for user feedback."""
    message_id: UUIDField = Field(
        ...,
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    user_id: UUIDField = Field(
        ...,
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    rating: FeedbackRatingField = Field(
        ...,
        examples=["positive"]
    )


@router.post("/api/feedback", status_code=status.HTTP_201_CREATED)
async def create_feedback(feedback: FeedbackCreate, db=Depends(get_db_client)):
    feedback_collection = db.feedback
    feedback_entry = {
        "message_id": feedback.message_id,
        "user_id": feedback.user_id,
        "rating": feedback.rating,
        "timestamp": datetime.now(UTC),
    }
    feedback_collection.insert_one(feedback_entry)
    return {"message": "Feedback received."}
