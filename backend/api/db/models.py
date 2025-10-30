"""MongoDB document schemas and helper functions for UP2D8 platform.

This module provides document schemas and utilities for working with MongoDB
collections. Unlike SQLAlchemy, MongoDB doesn't require strict schemas, but
these help maintain consistency and provide type hints.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any


# ============================================================================
# Helper Functions
# ============================================================================


def generate_uuid() -> str:
    """Generate UUID string for document IDs."""
    return str(uuid.uuid4())


def get_current_timestamp() -> datetime:
    """Get current UTC timestamp."""
    return datetime.utcnow()


# ============================================================================
# Document Schema Helpers
# ============================================================================


class UserDocument:
    """User document schema."""

    @staticmethod
    def create(
        email: str,
        password_hash: str,
        full_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new user document."""
        return {
            "id": kwargs.get("id", generate_uuid()),
            "email": email,
            "email_verified": False,
            "password_hash": password_hash,
            "full_name": full_name,
            "tier": kwargs.get("tier", "free"),
            "status": kwargs.get("status", "active"),
            "onboarding_completed": False,
            "oauth_provider": None,
            "oauth_id": None,
            "stripe_customer_id": None,
            "referral_code": None,
            "referred_by_user_id": None,
            "metadata": {},
            "created_at": get_current_timestamp(),
            "updated_at": get_current_timestamp(),
            "last_login_at": None,
        }


class UserPreferenceDocument:
    """User preference document schema."""

    @staticmethod
    def create(user_id: str, **kwargs) -> Dict[str, Any]:
        """Create a new user preference document."""
        return {
            "id": kwargs.get("id", generate_uuid()),
            "user_id": user_id,
            "subscribed_companies": [],
            "subscribed_industries": [],
            "subscribed_technologies": [],
            "subscribed_people": [],
            "digest_frequency": "daily",
            "delivery_time": "08:00:00",
            "timezone": "America/New_York",
            "delivery_days": [1, 2, 3, 4, 5],  # Mon-Fri
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
            "created_at": get_current_timestamp(),
            "updated_at": get_current_timestamp(),
        }


class ArticleDocument:
    """Article document schema."""

    @staticmethod
    def create(
        source_id: str,
        source_url: str,
        title: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new article document."""
        return {
            "id": kwargs.get("id", generate_uuid()),
            "source_id": source_id,
            "source_url": source_url,
            "source_type": kwargs.get("source_type"),
            "title": title,
            "content": kwargs.get("content"),
            "content_html": kwargs.get("content_html"),
            "summary_micro": kwargs.get("summary_micro"),
            "summary_standard": kwargs.get("summary_standard"),
            "summary_detailed": kwargs.get("summary_detailed"),
            "author": kwargs.get("author"),
            "published_at": kwargs.get("published_at"),
            "fetched_at": get_current_timestamp(),
            "updated_at": get_current_timestamp(),
            "companies": [],
            "industries": [],
            "technologies": [],
            "people": [],
            "categories": [],
            "impact_score": kwargs.get("impact_score"),
            "quality_score": kwargs.get("quality_score"),
            "engagement_score": 0,
            "sentiment": kwargs.get("sentiment"),
            "processing_status": "pending",
            "error_message": None,
            "content_hash": kwargs.get("content_hash"),
            "duplicate_of": None,
            "canonical": True,
            "metadata": {},
            "extracted_data": {},
        }


class SourceDocument:
    """Source document schema."""

    @staticmethod
    def create(
        source_id: str,
        name: str,
        source_type: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new source document."""
        return {
            "id": source_id,
            "name": name,
            "type": source_type,
            "url": kwargs.get("url"),
            "config": kwargs.get("config", {}),
            "check_interval_hours": kwargs.get("check_interval_hours", 6),
            "last_checked_at": None,
            "next_check_at": None,
            "priority": kwargs.get("priority", "medium"),
            "authority_score": kwargs.get("authority_score", 50),
            "success_count": 0,
            "failure_count": 0,
            "last_error": None,
            "companies": [],
            "industries": [],
            "active": True,
            "created_at": get_current_timestamp(),
            "updated_at": get_current_timestamp(),
        }


class DigestDocument:
    """Digest document schema."""

    @staticmethod
    def create(
        user_id: str,
        digest_date: str,
        scheduled_for: datetime,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new digest document."""
        return {
            "id": kwargs.get("id", generate_uuid()),
            "user_id": user_id,
            "digest_date": digest_date,
            "generated_at": get_current_timestamp(),
            "scheduled_for": scheduled_for,
            "sent_at": None,
            "user_preferences_snapshot": kwargs.get("user_preferences_snapshot", {}),
            "article_count": kwargs.get("article_count", 0),
            "personalized_intro": kwargs.get("personalized_intro"),
            "delivery_status": "pending",
            "delivery_error": None,
            "opened_at": None,
            "first_click_at": None,
            "total_clicks": 0,
            "chat_engaged": False,
            "email_subject": kwargs.get("email_subject"),
            "email_html": kwargs.get("email_html"),
            "email_plaintext": kwargs.get("email_plaintext"),
            "items": [],  # List of digest items
        }


class DigestItemDocument:
    """Digest item sub-document schema."""

    @staticmethod
    def create(
        article_id: str,
        position: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new digest item sub-document."""
        return {
            "id": kwargs.get("id", generate_uuid()),
            "article_id": article_id,
            "position": position,
            "relevance_score": kwargs.get("relevance_score"),
            "scoring_factors": kwargs.get("scoring_factors", {}),
            "clicked": False,
            "clicked_at": None,
            "chat_opened": False,
        }


class ChatSessionDocument:
    """Chat session document schema."""

    @staticmethod
    def create(user_id: str, **kwargs) -> Dict[str, Any]:
        """Create a new chat session document."""
        return {
            "id": kwargs.get("id", generate_uuid()),
            "user_id": user_id,
            "context_type": kwargs.get("context_type"),
            "context_id": kwargs.get("context_id"),
            "created_at": get_current_timestamp(),
            "last_message_at": get_current_timestamp(),
            "message_count": 0,
            "total_tokens_used": 0,
            "total_cost_usd": 0,
            "status": "active",
            "summary": None,
            "topics": [],
        }


class ChatMessageDocument:
    """Chat message document schema."""

    @staticmethod
    def create(
        session_id: str,
        role: str,
        content: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new chat message document."""
        return {
            "id": kwargs.get("id", generate_uuid()),
            "session_id": session_id,
            "role": role,
            "content": content,
            "retrieved_articles": kwargs.get("retrieved_articles", []),
            "web_search_results": kwargs.get("web_search_results"),
            "created_at": get_current_timestamp(),
            "tokens_used": kwargs.get("tokens_used"),
            "latency_ms": kwargs.get("latency_ms"),
            "feedback_score": None,
            "feedback_comment": None,
        }


class BookmarkDocument:
    """Bookmark document schema."""

    @staticmethod
    def create(
        user_id: str,
        article_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new bookmark document."""
        return {
            "id": kwargs.get("id", generate_uuid()),
            "user_id": user_id,
            "article_id": article_id,
            "tags": [],
            "notes": kwargs.get("notes"),
            "created_at": get_current_timestamp(),
        }


class ArticleFeedbackDocument:
    """Article feedback document schema."""

    @staticmethod
    def create(
        user_id: str,
        article_id: str,
        feedback_type: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new article feedback document."""
        return {
            "id": kwargs.get("id", generate_uuid()),
            "user_id": user_id,
            "article_id": article_id,
            "digest_id": kwargs.get("digest_id"),
            "feedback_type": feedback_type,
            "feedback_text": kwargs.get("feedback_text"),
            "feedback_source": kwargs.get("feedback_source", "email"),
            "created_at": get_current_timestamp(),
        }


# ============================================================================
# Collection Names
# ============================================================================

class Collections:
    """MongoDB collection name constants."""
    USERS = "users"
    USER_PREFERENCES = "user_preferences"
    ARTICLES = "articles"
    SOURCES = "sources"
    DIGESTS = "digests"
    CHAT_SESSIONS = "chat_sessions"
    CHAT_MESSAGES = "chat_messages"
    BOOKMARKS = "bookmarks"
    SUBSCRIPTIONS = "subscriptions"
    EMAIL_EVENTS = "email_events"
    USER_ACTIVITY = "user_activity"
    ARTICLE_FEEDBACK = "article_feedback"
    USER_PREFERENCE_PROFILE = "user_preference_profile"
    USER_ENGAGEMENT_METRICS = "user_engagement_metrics"
