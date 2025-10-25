"""Pydantic models for user preferences."""

from datetime import time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class PreferenceUpdate(BaseModel):
    """Model for updating user preferences."""

    # Subscription preferences
    subscribed_companies: Optional[List[str]] = Field(None, description="List of company names to follow")
    subscribed_industries: Optional[List[str]] = Field(None, description="List of industries to follow")
    subscribed_technologies: Optional[List[str]] = Field(None, description="List of technologies to follow")
    subscribed_people: Optional[List[str]] = Field(None, description="List of people to follow")

    # Delivery preferences
    digest_frequency: Optional[str] = Field(None, description="Frequency: daily, twice_daily, hourly, realtime")
    delivery_time: Optional[str] = Field(None, description="Time to deliver digest (HH:MM format, 24-hour)")
    timezone: Optional[str] = Field(None, description="User timezone (e.g., America/New_York)")
    delivery_days: Optional[List[int]] = Field(None, description="Days to deliver (1=Mon, 7=Sun)")

    # Format preferences
    email_format: Optional[str] = Field(None, description="Email format: html or text")
    article_count_per_digest: Optional[int] = Field(None, ge=1, le=20, description="Number of articles per digest")
    summary_style: Optional[str] = Field(None, description="Summary style: micro, standard, detailed")

    # Notification preferences
    notification_preferences: Optional[Dict[str, bool]] = Field(None, description="Notification settings")

    # Content preferences
    content_filters: Optional[Dict[str, Any]] = Field(None, description="Content filtering rules")

    @field_validator("digest_frequency")
    @classmethod
    def validate_digest_frequency(cls, v):
        """Validate digest frequency."""
        if v is not None:
            allowed = ["daily", "twice_daily", "hourly", "realtime"]
            if v not in allowed:
                raise ValueError(f"digest_frequency must be one of: {', '.join(allowed)}")
        return v

    @field_validator("email_format")
    @classmethod
    def validate_email_format(cls, v):
        """Validate email format."""
        if v is not None:
            allowed = ["html", "text"]
            if v not in allowed:
                raise ValueError(f"email_format must be one of: {', '.join(allowed)}")
        return v

    @field_validator("summary_style")
    @classmethod
    def validate_summary_style(cls, v):
        """Validate summary style."""
        if v is not None:
            allowed = ["micro", "standard", "detailed"]
            if v not in allowed:
                raise ValueError(f"summary_style must be one of: {', '.join(allowed)}")
        return v

    @field_validator("delivery_time")
    @classmethod
    def validate_delivery_time(cls, v):
        """Validate delivery time format."""
        if v is not None:
            try:
                # Parse HH:MM format
                parts = v.split(":")
                if len(parts) != 2:
                    raise ValueError
                hour = int(parts[0])
                minute = int(parts[1])
                if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                    raise ValueError
            except (ValueError, AttributeError):
                raise ValueError("delivery_time must be in HH:MM format (00:00 to 23:59)")
        return v

    @field_validator("delivery_days")
    @classmethod
    def validate_delivery_days(cls, v):
        """Validate delivery days."""
        if v is not None:
            if not all(1 <= day <= 7 for day in v):
                raise ValueError("delivery_days must contain values between 1 (Monday) and 7 (Sunday)")
            if len(v) == 0:
                raise ValueError("delivery_days must contain at least one day")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "subscribed_companies": ["OpenAI", "Anthropic", "Google"],
                "subscribed_industries": ["AI", "Machine Learning"],
                "delivery_time": "08:00",
                "timezone": "America/New_York",
                "delivery_days": [1, 2, 3, 4, 5],
                "article_count_per_digest": 7,
            }
        }


class PreferenceResponse(BaseModel):
    """Model for preference response."""

    # Subscription preferences
    subscribed_companies: List[str]
    subscribed_industries: List[str]
    subscribed_technologies: List[str]
    subscribed_people: List[str]

    # Delivery preferences
    digest_frequency: str
    delivery_time: str  # Converted to string for JSON
    timezone: str
    delivery_days: List[int]

    # Format preferences
    email_format: str
    article_count_per_digest: int
    summary_style: str

    # Notification preferences
    notification_preferences: Dict[str, bool]

    # Content preferences
    content_filters: Dict[str, Any]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "subscribed_companies": ["OpenAI", "Anthropic"],
                "subscribed_industries": ["AI"],
                "subscribed_technologies": ["GPT", "Claude"],
                "subscribed_people": [],
                "digest_frequency": "daily",
                "delivery_time": "08:00:00",
                "timezone": "America/New_York",
                "delivery_days": [1, 2, 3, 4, 5],
                "email_format": "html",
                "article_count_per_digest": 7,
                "summary_style": "standard",
                "notification_preferences": {
                    "breaking_news": True,
                    "weekly_summary": True,
                    "product_updates": False,
                    "marketing": False,
                },
                "content_filters": {
                    "min_impact_score": 3,
                    "exclude_topics": [],
                    "preferred_sources": [],
                    "language": "en",
                },
            }
        }
