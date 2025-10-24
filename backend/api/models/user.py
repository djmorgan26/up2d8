"""Pydantic models for User-related API operations."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from enum import Enum


class UserTier(str, Enum):
    """User subscription tiers."""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "active"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    DELETED = "deleted"


# ============================================================================
# Request Models (Input)
# ============================================================================


class UserCreate(BaseModel):
    """Request model for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=12, max_length=72)  # BCrypt max is 72 bytes
    full_name: str = Field(..., min_length=1, max_length=255)


class UserLogin(BaseModel):
    """Request model for user login."""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Request model for updating user profile."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    timezone: Optional[str] = None


class TokenRefresh(BaseModel):
    """Request model for refreshing access token."""
    refresh_token: str


class UserPreferencesUpdate(BaseModel):
    """Request model for updating user preferences."""
    subscribed_companies: Optional[List[str]] = None
    subscribed_industries: Optional[List[str]] = None
    subscribed_technologies: Optional[List[str]] = None
    subscribed_people: Optional[List[str]] = None
    digest_frequency: Optional[str] = Field(None, pattern="^(daily|twice_daily|hourly|realtime)$")
    delivery_time: Optional[str] = None  # HH:MM:SS format
    timezone: Optional[str] = None
    delivery_days: Optional[List[int]] = Field(None, min_length=1, max_length=7)
    email_format: Optional[str] = Field(None, pattern="^(html|plaintext|both)$")
    article_count_per_digest: Optional[int] = Field(None, ge=3, le=20)
    summary_style: Optional[str] = Field(None, pattern="^(micro|standard|detailed)$")
    notification_preferences: Optional[dict] = None
    content_filters: Optional[dict] = None


# ============================================================================
# Response Models (Output)
# ============================================================================


class UserResponse(BaseModel):
    """Response model for user data."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    full_name: str
    tier: UserTier
    status: UserStatus
    onboarding_completed: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None


class UserWithUsage(UserResponse):
    """Response model for user data with usage statistics."""
    usage: dict = Field(
        default_factory=lambda: {
            "chat_messages_today": 0,
            "chat_messages_limit": 10,  # Free tier default
            "digests_this_month": 0,
        }
    )


class TokenResponse(BaseModel):
    """Response model for authentication tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Seconds until access token expires


class AuthResponse(BaseModel):
    """Response model for authentication (login/signup)."""
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserPreferencesResponse(BaseModel):
    """Response model for user preferences."""
    model_config = ConfigDict(from_attributes=True)

    subscribed_companies: List[str] = []
    subscribed_industries: List[str] = []
    subscribed_technologies: List[str] = []
    subscribed_people: List[str] = []
    digest_frequency: str = "daily"
    delivery_time: str = "08:00:00"
    timezone: str = "America/New_York"
    delivery_days: List[int] = [1, 2, 3, 4, 5]
    email_format: str = "html"
    article_count_per_digest: int = 7
    summary_style: str = "standard"
    notification_preferences: dict = {}
    content_filters: dict = {}


class PreferencesUpdateResponse(BaseModel):
    """Response model for preference update operations."""
    message: str
    updated_fields: List[str]
    next_digest_at: Optional[datetime] = None
