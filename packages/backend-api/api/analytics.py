from datetime import UTC, datetime

from dependencies import get_db_client  # Import the new dependency
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

router = APIRouter(tags=["Analytics"])


class AnalyticsEvent(BaseModel):
    user_id: str
    event_type: str
    details: dict


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
