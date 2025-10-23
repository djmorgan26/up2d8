# Database Schema & API Specifications

## Document Information
- **Version**: 1.0
- **Last Updated**: October 23, 2025
- **Status**: Ready for Implementation

---

## Table of Contents
1. [Database Schema](#database-schema)
2. [API Endpoints](#api-endpoints)
3. [Data Models](#data-models)
4. [Example Payloads](#example-payloads)

---

## 1. Database Schema

### 1.1 Core Tables

#### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    password_hash VARCHAR(255), -- nullable for OAuth-only users
    full_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    tier VARCHAR(20) DEFAULT 'free' CHECK (tier IN ('free', 'pro', 'enterprise')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'suspended', 'deleted')),
    stripe_customer_id VARCHAR(100) UNIQUE,
    onboarding_completed BOOLEAN DEFAULT FALSE,
    referral_code VARCHAR(50) UNIQUE,
    referred_by_user_id UUID REFERENCES users(id),
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_tier ON users(tier);
CREATE INDEX idx_users_status ON users(status, tier);
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- Trigger to update updated_at
CREATE TRIGGER set_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

#### User Preferences Table
```sql
CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    
    -- Subscription preferences
    subscribed_companies TEXT[] DEFAULT '{}', -- e.g., ['openai', 'anthropic', 'google']
    subscribed_industries TEXT[] DEFAULT '{}', -- e.g., ['ai', 'semiconductors']
    subscribed_technologies TEXT[] DEFAULT '{}', -- e.g., ['llm', 'robotics']
    subscribed_people TEXT[] DEFAULT '{}', -- e.g., ['sam-altman', 'dario-amodei']
    
    -- Delivery preferences
    digest_frequency VARCHAR(20) DEFAULT 'daily' CHECK (digest_frequency IN ('daily', 'twice_daily', 'hourly', 'realtime')),
    delivery_time TIME DEFAULT '08:00:00', -- in user's timezone
    timezone VARCHAR(50) DEFAULT 'America/New_York',
    delivery_days INTEGER[] DEFAULT '{1,2,3,4,5}', -- 1=Monday, 7=Sunday; weekdays by default
    
    -- Format preferences
    email_format VARCHAR(20) DEFAULT 'html' CHECK (email_format IN ('html', 'plaintext', 'both')),
    article_count_per_digest INTEGER DEFAULT 7 CHECK (article_count_per_digest BETWEEN 3 AND 20),
    summary_style VARCHAR(20) DEFAULT 'standard' CHECK (summary_style IN ('micro', 'standard', 'detailed')),
    
    -- Notification preferences
    notification_preferences JSONB DEFAULT '{
        "breaking_news": true,
        "weekly_summary": true,
        "product_updates": false,
        "marketing": false
    }'::jsonb,
    
    -- Content preferences
    content_filters JSONB DEFAULT '{
        "min_impact_score": 3,
        "exclude_topics": [],
        "preferred_sources": [],
        "language": "en"
    }'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_user_prefs_delivery_time ON user_preferences(delivery_time, timezone);
CREATE INDEX idx_user_prefs_frequency ON user_preferences(digest_frequency);
```

#### Articles Table
```sql
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Source information
    source_id VARCHAR(100) NOT NULL, -- e.g., 'openai_blog', 'techcrunch'
    source_url TEXT UNIQUE NOT NULL,
    source_type VARCHAR(50), -- rss, api, scrape, github, social
    
    -- Content
    title TEXT NOT NULL,
    content TEXT, -- full article text
    content_html TEXT, -- original HTML if available
    summary_micro VARCHAR(280), -- tweet-length
    summary_standard TEXT, -- 150-200 words
    summary_detailed TEXT, -- 300-500 words
    
    -- Metadata
    author VARCHAR(255),
    published_at TIMESTAMP WITH TIME ZONE,
    fetched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Classifications
    companies TEXT[] DEFAULT '{}',
    industries TEXT[] DEFAULT '{}',
    technologies TEXT[] DEFAULT '{}',
    people TEXT[] DEFAULT '{}',
    categories TEXT[] DEFAULT '{}', -- press_release, blog, research, news, tutorial
    
    -- Scoring & quality
    impact_score INTEGER CHECK (impact_score BETWEEN 1 AND 10),
    quality_score DECIMAL(3,2) CHECK (quality_score BETWEEN 0 AND 1),
    engagement_score INTEGER DEFAULT 0, -- derived from user interactions
    sentiment VARCHAR(20) CHECK (sentiment IN ('positive', 'negative', 'neutral')),
    
    -- Vector embedding for semantic search
    embedding VECTOR(1536), -- assuming OpenAI ada-002 or similar
    
    -- Processing status
    processing_status VARCHAR(30) DEFAULT 'pending' CHECK (
        processing_status IN ('pending', 'processing', 'completed', 'failed', 'archived')
    ),
    error_message TEXT,
    
    -- Deduplication
    content_hash VARCHAR(64), -- SHA-256 hash of content for dedup
    duplicate_of UUID REFERENCES articles(id),
    canonical BOOLEAN DEFAULT TRUE,
    
    -- Rich metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    extracted_data JSONB DEFAULT '{}'::jsonb -- facts, quotes, dates extracted by LLM
);

-- Indexes
CREATE INDEX idx_articles_published_at ON articles(published_at DESC);
CREATE INDEX idx_articles_companies ON articles USING GIN(companies);
CREATE INDEX idx_articles_industries ON articles USING GIN(industries);
CREATE INDEX idx_articles_status ON articles(processing_status);
CREATE INDEX idx_articles_source ON articles(source_id, fetched_at DESC);
CREATE INDEX idx_articles_content_hash ON articles(content_hash);
CREATE INDEX idx_articles_impact ON articles(impact_score DESC, published_at DESC);

-- Vector index (specific syntax depends on extension: pgvector, pg_embedding, etc.)
CREATE INDEX idx_articles_embedding ON articles USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Full-text search
ALTER TABLE articles ADD COLUMN search_vector TSVECTOR;
CREATE INDEX idx_articles_search ON articles USING GIN(search_vector);

CREATE TRIGGER articles_search_update
BEFORE INSERT OR UPDATE ON articles
FOR EACH ROW
EXECUTE FUNCTION
tsvector_update_trigger(search_vector, 'pg_catalog.english', title, content, summary_standard);
```

#### Sources Table
```sql
CREATE TABLE sources (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- rss, api, scrape, github, social
    url TEXT,
    
    -- Scraping configuration
    config JSONB DEFAULT '{}'::jsonb, -- type-specific configuration
    
    -- Scheduling
    check_interval_hours INTEGER DEFAULT 6,
    last_checked_at TIMESTAMP WITH TIME ZONE,
    next_check_at TIMESTAMP WITH TIME ZONE,
    
    -- Reliability
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('high', 'medium', 'low')),
    authority_score INTEGER DEFAULT 50 CHECK (authority_score BETWEEN 0 AND 100),
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    last_error TEXT,
    
    -- Associations
    companies TEXT[] DEFAULT '{}',
    industries TEXT[] DEFAULT '{}',
    
    -- Status
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_sources_next_check ON sources(next_check_at) WHERE active = TRUE;
CREATE INDEX idx_sources_type ON sources(type);
```

#### Digests Table
```sql
CREATE TABLE digests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Digest metadata
    digest_date DATE NOT NULL,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    scheduled_for TIMESTAMP WITH TIME ZONE NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE,
    
    -- Personalization
    user_preferences_snapshot JSONB, -- capture preferences at generation time
    article_count INTEGER,
    personalized_intro TEXT, -- LLM-generated greeting
    
    -- Delivery
    delivery_status VARCHAR(30) DEFAULT 'pending' CHECK (
        delivery_status IN ('pending', 'queued', 'sent', 'delivered', 'bounced', 'failed')
    ),
    delivery_error TEXT,
    
    -- Engagement tracking
    opened_at TIMESTAMP WITH TIME ZONE,
    first_click_at TIMESTAMP WITH TIME ZONE,
    total_clicks INTEGER DEFAULT 0,
    chat_engaged BOOLEAN DEFAULT FALSE,
    
    -- Content
    email_subject VARCHAR(255),
    email_html TEXT,
    email_plaintext TEXT
);

CREATE INDEX idx_digests_user ON digests(user_id, digest_date DESC);
CREATE INDEX idx_digests_scheduled ON digests(scheduled_for) WHERE delivery_status = 'pending';
CREATE INDEX idx_digests_date ON digests(digest_date DESC);
CREATE UNIQUE INDEX idx_digests_user_date ON digests(user_id, digest_date);
```

#### Digest Items Table (Join table between digests and articles)
```sql
CREATE TABLE digest_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    digest_id UUID NOT NULL REFERENCES digests(id) ON DELETE CASCADE,
    article_id UUID NOT NULL REFERENCES articles(id),
    
    -- Position in digest
    position INTEGER NOT NULL, -- order of appearance
    
    -- Scoring details
    relevance_score DECIMAL(5,2), -- why this article was selected for this user
    scoring_factors JSONB, -- breakdown of scoring algorithm
    
    -- Engagement
    clicked BOOLEAN DEFAULT FALSE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    chat_opened BOOLEAN DEFAULT FALSE,
    
    UNIQUE(digest_id, article_id)
);

CREATE INDEX idx_digest_items_digest ON digest_items(digest_id, position);
CREATE INDEX idx_digest_items_article ON digest_items(article_id);
CREATE INDEX idx_digest_items_engagement ON digest_items(digest_id) WHERE clicked = TRUE;
```

#### Chat Sessions Table
```sql
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Context
    context_type VARCHAR(50), -- article, digest, general, onboarding
    context_id UUID, -- reference to article_id or digest_id if contextual
    
    -- Session metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    message_count INTEGER DEFAULT 0,
    
    -- Quality & costs
    total_tokens_used INTEGER DEFAULT 0,
    total_cost_usd DECIMAL(10,4) DEFAULT 0,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'abandoned')),
    
    -- Session summary (generated by LLM at end)
    summary TEXT,
    topics TEXT[]
);

CREATE INDEX idx_chat_sessions_user ON chat_sessions(user_id, last_message_at DESC);
CREATE INDEX idx_chat_sessions_context ON chat_sessions(context_type, context_id);
```

#### Chat Messages Table
```sql
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    
    -- Message content
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    
    -- Context used (for assistant messages)
    retrieved_articles UUID[], -- articles used for RAG
    web_search_results JSONB, -- if web search was performed
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tokens_used INTEGER,
    latency_ms INTEGER, -- response time
    
    -- Quality feedback
    feedback_score INTEGER CHECK (feedback_score IN (1, -1)), -- thumbs up/down
    feedback_comment TEXT
);

CREATE INDEX idx_chat_messages_session ON chat_messages(session_id, created_at);
CREATE INDEX idx_chat_messages_feedback ON chat_messages(feedback_score) WHERE feedback_score IS NOT NULL;
```

#### User Activity Table (Event log)
```sql
CREATE TABLE user_activity (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Event details
    event_type VARCHAR(100) NOT NULL,
    event_category VARCHAR(50), -- auth, digest, chat, preferences, billing
    
    -- Event data
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Session tracking
    session_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_activity_user ON user_activity(user_id, created_at DESC);
CREATE INDEX idx_activity_type ON user_activity(event_type, created_at DESC);
CREATE INDEX idx_activity_session ON user_activity(session_id);

-- Partition by month for scalability
-- (implement partitioning as data grows)
```

### 1.2 Supporting Tables

#### Subscriptions Table (Payment management)
```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Stripe integration
    stripe_subscription_id VARCHAR(100) UNIQUE,
    stripe_price_id VARCHAR(100),
    
    -- Plan details
    plan VARCHAR(50) NOT NULL, -- pro_monthly, pro_annual, enterprise_custom
    billing_interval VARCHAR(20), -- month, year
    
    -- Pricing
    price_usd DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Status
    status VARCHAR(30) NOT NULL CHECK (
        status IN ('active', 'trialing', 'past_due', 'canceled', 'incomplete', 'incomplete_expired', 'paused')
    ),
    
    -- Dates
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    trial_start TIMESTAMP WITH TIME ZONE,
    trial_end TIMESTAMP WITH TIME ZONE,
    canceled_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_period_end ON subscriptions(current_period_end)
    WHERE status IN ('active', 'trialing');
```

#### Email Events Table
```sql
CREATE TABLE email_events (
    id BIGSERIAL PRIMARY KEY,
    digest_id UUID REFERENCES digests(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Event type
    event_type VARCHAR(30) NOT NULL CHECK (
        event_type IN ('sent', 'delivered', 'opened', 'clicked', 'bounced', 'complained', 'unsubscribed')
    ),
    
    -- Event data
    email_address VARCHAR(255),
    link_url TEXT, -- for click events
    bounce_type VARCHAR(20), -- hard, soft
    error_message TEXT,
    
    -- Metadata
    message_id VARCHAR(255), -- from email service provider
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_email_events_digest ON email_events(digest_id, event_type);
CREATE INDEX idx_email_events_user ON email_events(user_id, event_type, created_at DESC);
CREATE INDEX idx_email_events_type ON email_events(event_type, created_at DESC);
```

#### Bookmarks Table
```sql
CREATE TABLE bookmarks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    
    -- Organization
    tags TEXT[] DEFAULT '{}',
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, article_id)
);

CREATE INDEX idx_bookmarks_user ON bookmarks(user_id, created_at DESC);
CREATE INDEX idx_bookmarks_article ON bookmarks(article_id);
```

---

## 2. API Endpoints

### 2.1 Authentication

#### POST /auth/signup
Register a new user

**Request:**
```json
{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "full_name": "John Doe"
}
```

**Response (201 Created):**
```json
{
    "user": {
        "id": "uuid",
        "email": "user@example.com",
        "full_name": "John Doe",
        "tier": "free",
        "created_at": "2025-10-23T10:00:00Z"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "expires_in": 900
}
```

**Errors:**
- 400: Email already exists
- 422: Invalid email format or password too weak

---

#### POST /auth/login
Authenticate user and get tokens

**Request:**
```json
{
    "email": "user@example.com",
    "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
    "user": {
        "id": "uuid",
        "email": "user@example.com",
        "full_name": "John Doe",
        "tier": "pro"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "expires_in": 900
}
```

**Errors:**
- 401: Invalid credentials
- 403: Account suspended

---

#### POST /auth/refresh
Refresh access token

**Request:**
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "expires_in": 900
}
```

---

#### POST /auth/logout
Invalidate tokens

**Request:** (requires Authorization header)
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (204 No Content)**

---

### 2.2 User Management

#### GET /users/me
Get current user profile

**Response (200 OK):**
```json
{
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "tier": "pro",
    "status": "active",
    "onboarding_completed": true,
    "created_at": "2025-10-23T10:00:00Z",
    "last_login_at": "2025-10-24T08:30:00Z",
    "usage": {
        "chat_messages_today": 42,
        "chat_messages_limit": 500,
        "digests_this_month": 24
    }
}
```

---

#### PUT /users/me
Update user profile

**Request:**
```json
{
    "full_name": "John A. Doe",
    "timezone": "America/Los_Angeles"
}
```

**Response (200 OK):**
```json
{
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John A. Doe",
    "updated_at": "2025-10-24T09:00:00Z"
}
```

---

#### GET /users/me/preferences
Get user preferences

**Response (200 OK):**
```json
{
    "subscribed_companies": ["openai", "anthropic", "google"],
    "subscribed_industries": ["ai", "robotics"],
    "subscribed_technologies": [],
    "digest_frequency": "daily",
    "delivery_time": "08:00:00",
    "timezone": "America/New_York",
    "delivery_days": [1, 2, 3, 4, 5],
    "email_format": "html",
    "article_count_per_digest": 7,
    "summary_style": "standard",
    "notification_preferences": {
        "breaking_news": true,
        "weekly_summary": true,
        "product_updates": false
    },
    "content_filters": {
        "min_impact_score": 5,
        "exclude_topics": ["cryptocurrency"],
        "preferred_sources": ["official"],
        "language": "en"
    }
}
```

---

#### PUT /users/me/preferences
Update user preferences

**Request:**
```json
{
    "subscribed_companies": ["openai", "anthropic", "nvidia", "microsoft"],
    "delivery_time": "07:30:00",
    "article_count_per_digest": 10
}
```

**Response (200 OK):**
```json
{
    "message": "Preferences updated successfully",
    "updated_fields": ["subscribed_companies", "delivery_time", "article_count_per_digest"],
    "next_digest_at": "2025-10-25T07:30:00-04:00"
}
```

---

### 2.3 Articles & Content

#### GET /articles
List articles with filters and pagination

**Query Parameters:**
- `companies[]`: Filter by company (repeatable)
- `industries[]`: Filter by industry
- `since`: ISO timestamp (only articles after this)
- `before`: ISO timestamp (only articles before this)
- `min_impact`: Minimum impact score (1-10)
- `page`: Page number (default: 1)
- `per_page`: Results per page (max: 100, default: 20)
- `sort`: Sort order (`published_at_desc`, `impact_desc`, `relevance`)

**Example Request:**
```
GET /articles?companies[]=openai&companies[]=anthropic&since=2025-10-20T00:00:00Z&page=1&per_page=20&sort=published_at_desc
```

**Response (200 OK):**
```json
{
    "articles": [
        {
            "id": "uuid",
            "title": "OpenAI Announces GPT-4.5",
            "summary_standard": "OpenAI released GPT-4.5, a major update featuring...",
            "source_id": "openai_blog",
            "source_url": "https://openai.com/blog/gpt-4.5",
            "published_at": "2025-10-23T14:00:00Z",
            "companies": ["openai"],
            "industries": ["ai", "saas"],
            "impact_score": 9,
            "sentiment": "positive",
            "engagement_score": 245
        },
        // ... more articles
    ],
    "pagination": {
        "page": 1,
        "per_page": 20,
        "total_pages": 12,
        "total_count": 234
    },
    "filters_applied": {
        "companies": ["openai", "anthropic"],
        "since": "2025-10-20T00:00:00Z"
    }
}
```

---

#### GET /articles/{article_id}
Get single article with full details

**Response (200 OK):**
```json
{
    "id": "uuid",
    "title": "OpenAI Announces GPT-4.5",
    "content": "Full article text here...",
    "summary_micro": "OpenAI released GPT-4.5 with 50% faster inference...",
    "summary_standard": "Detailed summary...",
    "summary_detailed": "Extended analysis...",
    "source_id": "openai_blog",
    "source_url": "https://openai.com/blog/gpt-4.5",
    "author": "Sam Altman",
    "published_at": "2025-10-23T14:00:00Z",
    "fetched_at": "2025-10-23T14:05:00Z",
    "companies": ["openai"],
    "industries": ["ai", "saas"],
    "technologies": ["llm", "machine-learning"],
    "people": ["sam-altman"],
    "categories": ["press_release", "product_launch"],
    "impact_score": 9,
    "quality_score": 0.95,
    "engagement_score": 245,
    "sentiment": "positive",
    "extracted_data": {
        "key_facts": [
            "50% faster inference",
            "12% improvement on MMLU benchmark",
            "30% cost reduction"
        ],
        "important_dates": ["2025-10-23"],
        "quotes": [
            {
                "text": "This is our fastest model yet",
                "speaker": "Sam Altman"
            }
        ]
    },
    "related_articles": [
        {
            "id": "uuid2",
            "title": "GPT-4 Performance Analysis",
            "similarity": 0.87
        }
    ],
    "is_bookmarked": false
}
```

---

#### POST /articles/{article_id}/bookmark
Bookmark an article

**Request:**
```json
{
    "tags": ["important", "for-team"],
    "notes": "Share this in Monday's standup"
}
```

**Response (201 Created):**
```json
{
    "bookmark_id": "uuid",
    "article_id": "uuid",
    "created_at": "2025-10-24T10:00:00Z"
}
```

---

#### DELETE /articles/{article_id}/bookmark
Remove bookmark

**Response (204 No Content)**

---

### 2.4 Digests

#### GET /digests
List user's digest history

**Query Parameters:**
- `since`: ISO date (YYYY-MM-DD)
- `before`: ISO date
- `page`: Page number
- `per_page`: Results per page (max: 50, default: 30)

**Response (200 OK):**
```json
{
    "digests": [
        {
            "id": "uuid",
            "digest_date": "2025-10-24",
            "generated_at": "2025-10-24T07:55:00Z",
            "sent_at": "2025-10-24T08:00:00Z",
            "delivery_status": "delivered",
            "opened_at": "2025-10-24T08:15:00Z",
            "article_count": 7,
            "total_clicks": 3,
            "chat_engaged": true,
            "email_subject": "Your Daily AI Industry Update - Oct 24"
        },
        // ... more digests
    ],
    "pagination": {
        "page": 1,
        "per_page": 30,
        "total_count": 87
    }
}
```

---

#### GET /digests/{digest_id}
Get detailed digest with articles

**Response (200 OK):**
```json
{
    "id": "uuid",
    "digest_date": "2025-10-24",
    "generated_at": "2025-10-24T07:55:00Z",
    "sent_at": "2025-10-24T08:00:00Z",
    "personalized_intro": "Good morning! Here's what happened in AI yesterday...",
    "articles": [
        {
            "position": 1,
            "article": {
                "id": "uuid",
                "title": "OpenAI Announces GPT-4.5",
                "summary_standard": "...",
                "source_url": "https://openai.com/blog/gpt-4.5",
                "published_at": "2025-10-23T14:00:00Z",
                "companies": ["openai"],
                "impact_score": 9
            },
            "relevance_score": 95.5,
            "clicked": true,
            "clicked_at": "2025-10-24T08:17:00Z"
        },
        // ... more articles
    ],
    "engagement": {
        "opened": true,
        "opened_at": "2025-10-24T08:15:00Z",
        "total_clicks": 3,
        "chat_opened": true
    }
}
```

---

#### POST /digests/preview
Generate preview digest (without sending)

**Request:**
```json
{
    "for_date": "2025-10-25",
    "preferences_override": {
        "article_count_per_digest": 5,
        "summary_style": "micro"
    }
}
```

**Response (200 OK):**
```json
{
    "preview_html": "<html>...</html>",
    "articles_selected": [/* array of articles */],
    "estimated_read_time_minutes": 8
}
```

---

### 2.5 Chat

#### POST /chat/sessions
Create new chat session

**Request:**
```json
{
    "context_type": "article",
    "context_id": "article-uuid"
}
```

**Response (201 Created):**
```json
{
    "session_id": "uuid",
    "created_at": "2025-10-24T10:30:00Z",
    "context": {
        "type": "article",
        "article": {
            "id": "uuid",
            "title": "OpenAI Announces GPT-4.5",
            "summary": "..."
        }
    }
}
```

---

#### POST /chat/sessions/{session_id}/messages
Send message in chat session

**Request:**
```json
{
    "message": "What are the key improvements in GPT-4.5?"
}
```

**Response (200 OK) - Streaming via Server-Sent Events:**
```
data: {"type": "chunk", "content": "The key"}
data: {"type": "chunk", "content": " improvements"}
data: {"type": "chunk", "content": " in GPT-4.5"}
data: {"type": "chunk", "content": " include:\n\n1. "}
...
data: {"type": "done", "message_id": "uuid", "tokens_used": 450, "citations": [{"article_id": "uuid", "title": "..."}]}
```

**Alternative Response (Non-streaming):**
```json
{
    "message_id": "uuid",
    "role": "assistant",
    "content": "The key improvements in GPT-4.5 include:\n\n1. 50% faster inference...",
    "citations": [
        {
            "article_id": "uuid",
            "title": "OpenAI Announces GPT-4.5",
            "url": "https://openai.com/blog/gpt-4.5"
        }
    ],
    "tokens_used": 450,
    "latency_ms": 1850,
    "suggested_followups": [
        "How does this compare to Claude 3.5?",
        "What's the pricing for GPT-4.5?",
        "Show me code examples using GPT-4.5"
    ]
}
```

---

#### GET /chat/sessions/{session_id}/messages
Get chat history

**Response (200 OK):**
```json
{
    "session_id": "uuid",
    "messages": [
        {
            "id": "msg-uuid-1",
            "role": "user",
            "content": "What are the key improvements?",
            "created_at": "2025-10-24T10:31:00Z"
        },
        {
            "id": "msg-uuid-2",
            "role": "assistant",
            "content": "The key improvements include...",
            "created_at": "2025-10-24T10:31:02Z",
            "citations": [/* ... */],
            "tokens_used": 450
        },
        // ... more messages
    ],
    "total_tokens_used": 1200,
    "total_cost_usd": 0.024
}
```

---

#### POST /chat/sessions/{session_id}/feedback
Provide feedback on assistant message

**Request:**
```json
{
    "message_id": "uuid",
    "score": 1,
    "comment": "Very helpful, thanks!"
}
```

**Response (200 OK):**
```json
{
    "message": "Feedback recorded"
}
```

---

### 2.6 Search

#### POST /search
Search articles semantically

**Request:**
```json
{
    "query": "latest developments in transformer architectures",
    "filters": {
        "companies": ["openai", "google", "anthropic"],
        "since": "2025-10-01",
        "min_impact_score": 5
    },
    "limit": 20
}
```

**Response (200 OK):**
```json
{
    "results": [
        {
            "article": {/* full article object */},
            "relevance_score": 0.92,
            "match_highlights": [
                "...new transformer architecture called...",
                "...efficiency improvements in attention mechanism..."
            ]
        },
        // ... more results
    ],
    "total_results": 45,
    "search_time_ms": 230
}
```

---

### 2.7 Subscriptions & Billing

#### GET /subscriptions/plans
List available plans

**Response (200 OK):**
```json
{
    "plans": [
        {
            "id": "pro_monthly",
            "name": "Pro Monthly",
            "price_usd": 19.00,
            "billing_interval": "month",
            "features": [
                "Unlimited company subscriptions",
                "Hourly digests available",
                "Unlimited AI chat",
                "Full dashboard access",
                "1-year history"
            ],
            "limits": {
                "chat_messages_per_day": 500,
                "api_requests_per_hour": 1000
            }
        },
        {
            "id": "pro_annual",
            "name": "Pro Annual",
            "price_usd": 190.00,
            "billing_interval": "year",
            "features": [/* same as pro_monthly */],
            "savings_percent": 16.7
        }
    ]
}
```

---

#### POST /subscriptions/checkout
Create Stripe checkout session for upgrade

**Request:**
```json
{
    "plan_id": "pro_monthly",
    "success_url": "https://app.insightstream.ai/success",
    "cancel_url": "https://app.insightstream.ai/pricing"
}
```

**Response (200 OK):**
```json
{
    "checkout_session_id": "cs_test_...",
    "checkout_url": "https://checkout.stripe.com/pay/cs_test_..."
}
```

---

#### POST /subscriptions/portal
Get Stripe customer portal URL

**Response (200 OK):**
```json
{
    "portal_url": "https://billing.stripe.com/session/..."
}
```

---

### 2.8 Admin & Analytics

#### GET /admin/stats
System-wide statistics (admin only)

**Response (200 OK):**
```json
{
    "users": {
        "total": 10450,
        "active_monthly": 8230,
        "active_daily": 5120,
        "by_tier": {
            "free": 8500,
            "pro": 1800,
            "enterprise": 150
        }
    },
    "articles": {
        "total": 125600,
        "processed_today": 380,
        "avg_processing_time_sec": 4.2
    },
    "digests": {
        "sent_today": 8000,
        "avg_open_rate": 0.63,
        "avg_click_rate": 0.28
    },
    "chat": {
        "sessions_today": 1200,
        "messages_today": 4500,
        "avg_session_length": 3.7
    },
    "costs": {
        "llm_api_cost_today_usd": 234.50,
        "email_cost_today_usd": 12.30,
        "infrastructure_cost_monthly_estimate_usd": 1500.00
    }
}
```

---

## 3. Data Models (Pydantic)

### User Models
```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class UserTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class UserStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=12)
    full_name: str = Field(..., min_length=1, max_length=255)

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    tier: UserTier
    status: UserStatus
    onboarding_completed: bool
    created_at: datetime
    last_login_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class UserPreferences(BaseModel):
    subscribed_companies: List[str] = []
    subscribed_industries: List[str] = []
    subscribed_technologies: List[str] = []
    digest_frequency: str = "daily"
    delivery_time: str = "08:00:00"
    timezone: str = "America/New_York"
    delivery_days: List[int] = [1, 2, 3, 4, 5]
    email_format: str = "html"
    article_count_per_digest: int = Field(default=7, ge=3, le=20)
    summary_style: str = "standard"
    notification_preferences: dict = {}
    content_filters: dict = {}
```

### Article Models
```python
class ArticleBase(BaseModel):
    title: str
    source_url: str
    summary_standard: Optional[str]
    published_at: datetime
    companies: List[str] = []
    industries: List[str] = []
    impact_score: Optional[int] = Field(None, ge=1, le=10)

class ArticleDetail(ArticleBase):
    id: str
    content: Optional[str]
    summary_micro: Optional[str]
    summary_detailed: Optional[str]
    author: Optional[str]
    technologies: List[str] = []
    people: List[str] = []
    categories: List[str] = []
    quality_score: Optional[float]
    engagement_score: int = 0
    sentiment: Optional[str]
    extracted_data: dict = {}
    is_bookmarked: bool = False
    
    class Config:
        from_attributes = True
```

### Chat Models
```python
class ChatMessageCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)

class ChatMessageResponse(BaseModel):
    message_id: str
    role: str
    content: str
    citations: List[dict] = []
    tokens_used: int
    latency_ms: int
    suggested_followups: List[str] = []
    created_at: datetime
    
class ChatSessionCreate(BaseModel):
    context_type: Optional[str] = None
    context_id: Optional[str] = None
```

---

## 4. Example Workflows

### 4.1 User Onboarding Flow

1. **User signs up**
   ```
   POST /auth/signup
   → Creates user with default preferences
   → Returns JWT tokens
   ```

2. **User sets preferences**
   ```
   PUT /users/me/preferences
   {
     "subscribed_companies": ["openai", "anthropic"],
     "delivery_time": "08:00:00",
     "timezone": "America/Los_Angeles"
   }
   ```

3. **System generates first digest**
   ```
   [Scheduled job runs at 7:55 AM PT]
   → Queries articles from last 24 hours matching user preferences
   → Ranks and selects top 7 articles
   → Generates personalized intro with LLM
   → Renders email template
   → Sends via SES at 8:00 AM PT
   ```

4. **User opens email**
   ```
   [Email client loads tracking pixel]
   → Registers 'opened' event
   → Updates digests.opened_at
   → Logs to email_events table
   ```

5. **User clicks article**
   ```
   [User clicks tracked link]
   → Redirects to article
   → Updates digest_items.clicked = true
   → Logs to email_events and user_activity
   ```

6. **User asks question**
   ```
   POST /chat/sessions
   {
     "context_type": "digest",
     "context_id": "<digest_uuid>"
   }
   → Creates session
   
   POST /chat/sessions/{id}/messages
   {
     "message": "Tell me more about the OpenAI announcement"
   }
   → Retrieves articles from digest using RAG
   → Generates response with Claude
   → Streams response to user
   ```

---

### 4.2 Article Processing Pipeline

1. **Scraper fetches new content**
   ```python
   @celery.task
   def fetch_source(source_id):
       source = get_source(source_id)
       new_articles = scraper.fetch(source)
       
       for article_data in new_articles:
           # Check if already exists
           existing = Article.query.filter_by(
               source_url=article_data['url']
           ).first()
           
           if not existing:
               # Store raw content
               article = Article(
                   source_id=source_id,
                   source_url=article_data['url'],
                   title=article_data['title'],
                   content=article_data['content'],
                   published_at=article_data['published_at'],
                   processing_status='pending'
               )
               db.session.add(article)
               db.session.commit()
               
               # Queue for processing
               process_article.delay(article.id)
   ```

2. **Article gets processed**
   ```python
   @celery.task
   def process_article(article_id):
       article = Article.query.get(article_id)
       
       # Generate summaries
       summaries = llm.generate_summaries(article.content)
       article.summary_micro = summaries['micro']
       article.summary_standard = summaries['standard']
       article.summary_detailed = summaries['detailed']
       
       # Extract entities and classify
       classification = llm.classify(article)
       article.companies = classification['companies']
       article.industries = classification['industries']
       article.impact_score = classification['impact_score']
       
       # Generate embedding
       embedding = embed(article.title + " " + article.summary_standard)
       article.embedding = embedding
       
       # Store in vector DB
       vector_db.upsert(
           id=article.id,
           vector=embedding,
           metadata={
               'title': article.title,
               'companies': article.companies,
               'published_at': article.published_at.isoformat()
           }
       )
       
       article.processing_status = 'completed'
       db.session.commit()
   ```

---

## 5. Rate Limits

### Per-Tier Limits

| Endpoint Category | Free | Pro | Enterprise |
|-------------------|------|-----|------------|
| API Requests | 100/hour | 1,000/hour | 10,000/hour |
| Chat Messages | 10/day | 500/day | Unlimited |
| Digest Deliveries | 1/day | 24/day | Unlimited |
| Search Queries | 20/hour | 200/hour | Unlimited |
| Bookmark Operations | 50/day | Unlimited | Unlimited |

### Rate Limit Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1698336000
```

### Rate Limit Exceeded Response (429)
```json
{
    "error": "rate_limit_exceeded",
    "message": "You have exceeded your chat message limit for today. Upgrade to Pro for higher limits.",
    "limit": 10,
    "reset_at": "2025-10-25T00:00:00Z",
    "upgrade_url": "https://app.insightstream.ai/pricing"
}
```

---

## 6. Webhook Events (Future)

### Webhook Payload Structure
```json
{
    "event_id": "evt_uuid",
    "event_type": "digest.sent",
    "created_at": "2025-10-24T08:00:00Z",
    "data": {
        "digest_id": "uuid",
        "user_id": "uuid",
        "article_count": 7,
        "sent_at": "2025-10-24T08:00:00Z"
    }
}
```

### Available Event Types
- `user.created`
- `user.upgraded`
- `user.downgraded`
- `digest.generated`
- `digest.sent`
- `digest.opened`
- `chat.session_created`
- `chat.message_sent`
- `subscription.created`
- `subscription.canceled`

---

**Document Version**: 1.0  
**Last Updated**: October 23, 2025  
**Status**: Ready for Implementation
