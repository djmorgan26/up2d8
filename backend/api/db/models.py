"""SQLAlchemy database models for UP2D8 platform.

Based on database schema specification in docs/planning/database-api-spec.md
"""

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import (
    Boolean,
    Column,
    String,
    Integer,
    Text,
    TIMESTAMP,
    ForeignKey,
    CheckConstraint,
    Index,
    ARRAY,
    DECIMAL,
    Date,
    Time,
    BIGINT,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .session import Base


# Helper function for UUID primary keys
def generate_uuid():
    """Generate UUID for primary keys."""
    return str(uuid.uuid4())


# ============================================================================
# CORE TABLES
# ============================================================================


class User(Base):
    """User accounts table."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    email_verified = Column(Boolean, default=False)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth-only users
    full_name = Column(String(255))

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Account status
    tier = Column(String(20), default="free", nullable=False)
    status = Column(String(20), default="active", nullable=False)

    # Billing
    stripe_customer_id = Column(String(100), unique=True, nullable=True)

    # Onboarding
    onboarding_completed = Column(Boolean, default=False)

    # Referrals
    referral_code = Column(String(50), unique=True, nullable=True)
    referred_by_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)

    # Metadata (use extra_metadata to avoid SQLAlchemy reserved name)
    extra_metadata = Column("metadata", JSONB, default={})

    # Constraints
    __table_args__ = (
        CheckConstraint("tier IN ('free', 'pro', 'enterprise')", name="check_user_tier"),
        CheckConstraint("status IN ('active', 'paused', 'suspended', 'deleted')", name="check_user_status"),
        Index("idx_users_tier", "tier"),
        Index("idx_users_status", "status", "tier"),
        Index("idx_users_created_at", created_at.desc()),
    )

    # Relationships
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    digests = relationship("Digest", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")


class UserPreference(Base):
    """User preferences for content and delivery."""

    __tablename__ = "user_preferences"

    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    # Subscription preferences
    subscribed_companies = Column(ARRAY(Text), default=[])
    subscribed_industries = Column(ARRAY(Text), default=[])
    subscribed_technologies = Column(ARRAY(Text), default=[])
    subscribed_people = Column(ARRAY(Text), default=[])

    # Delivery preferences
    digest_frequency = Column(String(20), default="daily")
    delivery_time = Column(Time, default="08:00:00")
    timezone = Column(String(50), default="America/New_York")
    delivery_days = Column(ARRAY(Integer), default=[1, 2, 3, 4, 5])  # Mon-Fri

    # Format preferences
    email_format = Column(String(20), default="html")
    article_count_per_digest = Column(Integer, default=7)
    summary_style = Column(String(20), default="standard")

    # Notification preferences
    notification_preferences = Column(
        JSONB,
        default={
            "breaking_news": True,
            "weekly_summary": True,
            "product_updates": False,
            "marketing": False,
        },
    )

    # Content preferences
    content_filters = Column(
        JSONB,
        default={
            "min_impact_score": 3,
            "exclude_topics": [],
            "preferred_sources": [],
            "language": "en",
        },
    )

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "digest_frequency IN ('daily', 'twice_daily', 'hourly', 'realtime')",
            name="check_digest_frequency",
        ),
        CheckConstraint(
            "email_format IN ('html', 'plaintext', 'both')",
            name="check_email_format",
        ),
        CheckConstraint(
            "summary_style IN ('micro', 'standard', 'detailed')",
            name="check_summary_style",
        ),
        CheckConstraint(
            "article_count_per_digest BETWEEN 3 AND 20",
            name="check_article_count",
        ),
        Index("idx_user_prefs_delivery_time", "delivery_time", "timezone"),
        Index("idx_user_prefs_frequency", "digest_frequency"),
    )

    # Relationships
    user = relationship("User", back_populates="preferences")


class Article(Base):
    """Articles fetched from various sources."""

    __tablename__ = "articles"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)

    # Source information
    source_id = Column(String(100), ForeignKey("sources.id"), nullable=False)
    source_url = Column(Text, unique=True, nullable=False)
    source_type = Column(String(50))  # rss, api, scrape, github, social

    # Content
    title = Column(Text, nullable=False)
    content = Column(Text)  # Full article text
    content_html = Column(Text)  # Original HTML
    summary_micro = Column(String(280))  # Tweet-length
    summary_standard = Column(Text)  # 150-200 words
    summary_detailed = Column(Text)  # 300-500 words

    # Metadata
    author = Column(String(255))
    published_at = Column(TIMESTAMP(timezone=True))
    fetched_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Classifications
    companies = Column(ARRAY(Text), default=[])
    industries = Column(ARRAY(Text), default=[])
    technologies = Column(ARRAY(Text), default=[])
    people = Column(ARRAY(Text), default=[])
    categories = Column(ARRAY(Text), default=[])

    # Scoring & quality
    impact_score = Column(Integer)
    quality_score = Column(DECIMAL(3, 2))
    engagement_score = Column(Integer, default=0)
    sentiment = Column(String(20))

    # Processing status
    processing_status = Column(String(30), default="pending")
    error_message = Column(Text)

    # Deduplication
    content_hash = Column(String(64))  # SHA-256 hash
    duplicate_of = Column(UUID(as_uuid=False), ForeignKey("articles.id"), nullable=True)
    canonical = Column(Boolean, default=True)

    # Rich metadata (use extra_metadata to avoid SQLAlchemy reserved name)
    extra_metadata = Column("metadata", JSONB, default={})
    extracted_data = Column(JSONB, default={})

    # Constraints
    __table_args__ = (
        CheckConstraint("impact_score BETWEEN 1 AND 10", name="check_impact_score"),
        CheckConstraint("quality_score BETWEEN 0 AND 1", name="check_quality_score"),
        CheckConstraint("sentiment IN ('positive', 'negative', 'neutral')", name="check_sentiment"),
        CheckConstraint(
            "processing_status IN ('pending', 'processing', 'completed', 'failed', 'archived')",
            name="check_processing_status",
        ),
        Index("idx_articles_published_at", published_at.desc()),
        Index("idx_articles_companies", "companies", postgresql_using="gin"),
        Index("idx_articles_industries", "industries", postgresql_using="gin"),
        Index("idx_articles_status", "processing_status"),
        Index("idx_articles_source", "source_id", fetched_at.desc()),
        Index("idx_articles_content_hash", "content_hash"),
        Index("idx_articles_impact", impact_score.desc(), published_at.desc()),
    )

    # Relationships
    source = relationship("Source", back_populates="articles")
    digest_items = relationship("DigestItem", back_populates="article")
    bookmarks = relationship("Bookmark", back_populates="article", cascade="all, delete-orphan")


class Source(Base):
    """Content sources for scraping."""

    __tablename__ = "sources"

    id = Column(String(100), primary_key=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # rss, api, scrape, github, social
    url = Column(Text)

    # Scraping configuration
    config = Column(JSONB, default={})

    # Scheduling
    check_interval_hours = Column(Integer, default=6)
    last_checked_at = Column(TIMESTAMP(timezone=True))
    next_check_at = Column(TIMESTAMP(timezone=True))

    # Reliability
    priority = Column(String(20), default="medium")
    authority_score = Column(Integer, default=50)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    last_error = Column(Text)

    # Associations
    companies = Column(ARRAY(Text), default=[])
    industries = Column(ARRAY(Text), default=[])

    # Status
    active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint("priority IN ('high', 'medium', 'low')", name="check_priority"),
        CheckConstraint("authority_score BETWEEN 0 AND 100", name="check_authority_score"),
        Index("idx_sources_next_check", "next_check_at", postgresql_where=Column("active") == True),
        Index("idx_sources_type", "type"),
    )

    # Relationships
    articles = relationship("Article", back_populates="source")


class Digest(Base):
    """Daily digests sent to users."""

    __tablename__ = "digests"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Digest metadata
    digest_date = Column(Date, nullable=False)
    generated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    scheduled_for = Column(TIMESTAMP(timezone=True), nullable=False)
    sent_at = Column(TIMESTAMP(timezone=True))

    # Personalization
    user_preferences_snapshot = Column(JSONB)
    article_count = Column(Integer)
    personalized_intro = Column(Text)

    # Delivery
    delivery_status = Column(String(30), default="pending")
    delivery_error = Column(Text)

    # Engagement tracking
    opened_at = Column(TIMESTAMP(timezone=True))
    first_click_at = Column(TIMESTAMP(timezone=True))
    total_clicks = Column(Integer, default=0)
    chat_engaged = Column(Boolean, default=False)

    # Content
    email_subject = Column(String(255))
    email_html = Column(Text)
    email_plaintext = Column(Text)

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "delivery_status IN ('pending', 'queued', 'sent', 'delivered', 'bounced', 'failed')",
            name="check_delivery_status",
        ),
        Index("idx_digests_user", "user_id", digest_date.desc()),
        Index("idx_digests_scheduled", "scheduled_for", postgresql_where=Column("delivery_status") == "pending"),
        Index("idx_digests_date", digest_date.desc()),
        Index("idx_digests_user_date", "user_id", "digest_date", unique=True),
    )

    # Relationships
    user = relationship("User", back_populates="digests")
    items = relationship("DigestItem", back_populates="digest", cascade="all, delete-orphan")


class DigestItem(Base):
    """Articles included in digests (join table)."""

    __tablename__ = "digest_items"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    digest_id = Column(UUID(as_uuid=False), ForeignKey("digests.id", ondelete="CASCADE"), nullable=False)
    article_id = Column(UUID(as_uuid=False), ForeignKey("articles.id"), nullable=False)

    # Position in digest
    position = Column(Integer, nullable=False)

    # Scoring details
    relevance_score = Column(DECIMAL(5, 2))
    scoring_factors = Column(JSONB)

    # Engagement
    clicked = Column(Boolean, default=False)
    clicked_at = Column(TIMESTAMP(timezone=True))
    chat_opened = Column(Boolean, default=False)

    # Constraints
    __table_args__ = (
        Index("idx_digest_items_digest", "digest_id", "position"),
        Index("idx_digest_items_article", "article_id"),
        Index("idx_digest_items_engagement", "digest_id", postgresql_where=Column("clicked") == True),
        Index("idx_digest_items_unique", "digest_id", "article_id", unique=True),
    )

    # Relationships
    digest = relationship("Digest", back_populates="items")
    article = relationship("Article", back_populates="digest_items")


class ChatSession(Base):
    """Chat sessions for RAG conversations."""

    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Context
    context_type = Column(String(50))  # article, digest, general, onboarding
    context_id = Column(UUID(as_uuid=False))

    # Session metadata
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_message_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    message_count = Column(Integer, default=0)

    # Quality & costs
    total_tokens_used = Column(Integer, default=0)
    total_cost_usd = Column(DECIMAL(10, 4), default=0)

    # Status
    status = Column(String(20), default="active")

    # Session summary
    summary = Column(Text)
    topics = Column(ARRAY(Text))

    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('active', 'archived', 'abandoned')", name="check_session_status"),
        Index("idx_chat_sessions_user", "user_id", last_message_at.desc()),
        Index("idx_chat_sessions_context", "context_type", "context_id"),
    )

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Individual messages in chat sessions."""

    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    session_id = Column(UUID(as_uuid=False), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)

    # Message content
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)

    # Context used (for assistant messages)
    retrieved_articles = Column(ARRAY(UUID(as_uuid=False)))
    web_search_results = Column(JSONB)

    # Metadata
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    tokens_used = Column(Integer)
    latency_ms = Column(Integer)

    # Quality feedback
    feedback_score = Column(Integer)  # 1 (thumbs up) or -1 (thumbs down)
    feedback_comment = Column(Text)

    # Constraints
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system')", name="check_message_role"),
        CheckConstraint("feedback_score IN (1, -1)", name="check_feedback_score"),
        Index("idx_chat_messages_session", "session_id", created_at),
        Index("idx_chat_messages_feedback", "feedback_score", postgresql_where=Column("feedback_score").isnot(None)),
    )

    # Relationships
    session = relationship("ChatSession", back_populates="messages")


# ============================================================================
# SUPPORTING TABLES
# ============================================================================


class Subscription(Base):
    """Payment subscriptions."""

    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Stripe integration
    stripe_subscription_id = Column(String(100), unique=True)
    stripe_price_id = Column(String(100))

    # Plan details
    plan = Column(String(50), nullable=False)
    billing_interval = Column(String(20))

    # Pricing
    price_usd = Column(DECIMAL(10, 2))
    currency = Column(String(3), default="USD")

    # Status
    status = Column(String(30), nullable=False)

    # Dates
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    current_period_start = Column(TIMESTAMP(timezone=True))
    current_period_end = Column(TIMESTAMP(timezone=True))
    trial_start = Column(TIMESTAMP(timezone=True))
    trial_end = Column(TIMESTAMP(timezone=True))
    canceled_at = Column(TIMESTAMP(timezone=True))
    ended_at = Column(TIMESTAMP(timezone=True))

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'trialing', 'past_due', 'canceled', 'incomplete', 'incomplete_expired', 'paused')",
            name="check_subscription_status",
        ),
        Index("idx_subscriptions_user", "user_id"),
        Index("idx_subscriptions_status", "status"),
        Index(
            "idx_subscriptions_period_end",
            "current_period_end",
            postgresql_where=Column("status").in_(["active", "trialing"]),
        ),
    )

    # Relationships
    user = relationship("User", back_populates="subscriptions")


class EmailEvent(Base):
    """Email delivery and engagement events."""

    __tablename__ = "email_events"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    digest_id = Column(UUID(as_uuid=False), ForeignKey("digests.id", ondelete="SET NULL"))
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"))

    # Event type
    event_type = Column(String(30), nullable=False)

    # Event data
    email_address = Column(String(255))
    link_url = Column(Text)
    bounce_type = Column(String(20))
    error_message = Column(Text)

    # Metadata (use extra_metadata to avoid SQLAlchemy reserved name)
    message_id = Column(String(255))
    extra_metadata = Column("metadata", JSONB, default={})

    # Timestamp
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "event_type IN ('sent', 'delivered', 'opened', 'clicked', 'bounced', 'complained', 'unsubscribed')",
            name="check_email_event_type",
        ),
        Index("idx_email_events_digest", "digest_id", "event_type"),
        Index("idx_email_events_user", "user_id", "event_type", created_at.desc()),
        Index("idx_email_events_type", "event_type", created_at.desc()),
    )


class Bookmark(Base):
    """User bookmarks for articles."""

    __tablename__ = "bookmarks"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    article_id = Column(UUID(as_uuid=False), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)

    # Organization
    tags = Column(ARRAY(Text), default=[])
    notes = Column(Text)

    # Timestamp
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Constraints
    __table_args__ = (
        Index("idx_bookmarks_user", "user_id", created_at.desc()),
        Index("idx_bookmarks_article", "article_id"),
        Index("idx_bookmarks_unique", "user_id", "article_id", unique=True),
    )

    # Relationships
    user = relationship("User", back_populates="bookmarks")
    article = relationship("Article", back_populates="bookmarks")


class UserActivity(Base):
    """User activity event log."""

    __tablename__ = "user_activity"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"))

    # Event details
    event_type = Column(String(100), nullable=False)
    event_category = Column(String(50))  # auth, digest, chat, preferences, billing

    # Event data (use extra_metadata to avoid SQLAlchemy reserved name)
    extra_metadata = Column("metadata", JSONB, default={})

    # Session tracking
    session_id = Column(String(100))
    ip_address = Column(INET)
    user_agent = Column(Text)

    # Timestamp
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Constraints
    __table_args__ = (
        Index("idx_activity_user", "user_id", created_at.desc()),
        Index("idx_activity_type", "event_type", created_at.desc()),
        Index("idx_activity_session", "session_id"),
    )
