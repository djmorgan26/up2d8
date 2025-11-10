from datetime import UTC, datetime

from dependencies import get_db_client  # Import the new dependency
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from shared.validation import UUIDField, EventTypeField, DetailsField

router = APIRouter(tags=["Analytics"])


class AnalyticsEvent(BaseModel):
    """Request model for analytics events."""
    user_id: UUIDField = Field(
        ...,
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    event_type: EventTypeField = Field(
        ...,
        examples=["article_view"]
    )
    details: DetailsField = Field(
        ...,
        examples=[{"article_id": "123", "duration_seconds": 45}]
    )


@router.post("/api/analytics", status_code=status.HTTP_202_ACCEPTED)
async def create_analytics(event: AnalyticsEvent, db=Depends(get_db_client)):
    analytics_collection = db.analytics
    analytics_entry = {
        "user_id": event.user_id,
        "event_type": event.event_type,
        "details": event.details,
        "timestamp": datetime.now(UTC),
    }
    analytics_collection.insert_one(analytics_entry)
    return {"message": "Event logged."}
