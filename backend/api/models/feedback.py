"""
Pydantic models for article feedback system.
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
from uuid import UUID


class FeedbackCreate(BaseModel):
    """Request model for creating feedback."""

    article_id: UUID
    digest_id: Optional[UUID] = None
    feedback_type: Literal["thumbs_up", "thumbs_down", "not_relevant"]
    feedback_text: Optional[str] = Field(None, max_length=500)
    feedback_source: Literal["email", "web", "api"] = "web"

    class Config:
        json_schema_extra = {
            "example": {
                "article_id": "123e4567-e89b-12d3-a456-426614174000",
                "digest_id": "123e4567-e89b-12d3-a456-426614174001",
                "feedback_type": "thumbs_up",
                "feedback_text": "Very helpful article!",
                "feedback_source": "email"
            }
        }


class FeedbackResponse(BaseModel):
    """Response model for feedback."""

    id: UUID
    user_id: UUID
    article_id: UUID
    digest_id: Optional[UUID]
    feedback_type: str
    feedback_text: Optional[str]
    feedback_source: str
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackStats(BaseModel):
    """Statistics about user feedback."""

    total_feedback: int
    thumbs_up: int
    thumbs_down: int
    not_relevant: int
    feedback_rate: float  # percentage of articles that received feedback
    positive_rate: float  # percentage of thumbs up out of total feedback

    class Config:
        json_schema_extra = {
            "example": {
                "total_feedback": 42,
                "thumbs_up": 35,
                "thumbs_down": 5,
                "not_relevant": 2,
                "feedback_rate": 0.15,
                "positive_rate": 0.83
            }
        }


class UserPreferenceProfileResponse(BaseModel):
    """Response model for user preference profile."""

    user_id: UUID
    company_weights: dict
    industry_weights: dict
    topic_weights: dict
    total_feedback_count: int
    positive_feedback_count: int
    negative_feedback_count: int
    avg_engagement_score: float
    last_updated_at: datetime

    class Config:
        from_attributes = True


class EngagementMetricsResponse(BaseModel):
    """Response model for user engagement metrics."""

    user_id: UUID
    total_emails_sent: int
    total_emails_opened: int
    total_links_clicked: int
    total_articles_clicked: int
    avg_articles_clicked_per_digest: float
    open_rate: float
    click_rate: float
    engagement_score: float
    avg_time_to_open_seconds: int
    last_calculated_at: datetime

    class Config:
        from_attributes = True
