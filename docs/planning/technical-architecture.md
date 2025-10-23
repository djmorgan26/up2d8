# Technical Architecture Document: UP2D8 Platform

## Document Information
- **Version**: 1.0
- **Last Updated**: October 23, 2025
- **Owner**: Engineering Team
- **Status**: Design Phase

---

## 1. System Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                            │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│  Email Client│ Web Dashboard│  Mobile App  │  API Clients      │
│              │   (React)    │   (Future)   │  (Enterprise)     │
└──────┬───────┴──────┬───────┴──────┬───────┴──────┬────────────┘
       │              │              │              │
       │              └──────────────┴──────────────┤
       │                                            │
┌──────▼────────────────────────────────────────────▼─────────────┐
│                      API GATEWAY LAYER                           │
│              (FastAPI / Kong / AWS API Gateway)                  │
│    ┌──────────────┬──────────────┬──────────────────┐          │
│    │ Rate Limiting│ Auth/Session │ Request Routing  │          │
│    └──────────────┴──────────────┴──────────────────┘          │
└──────┬────────────────────────┬───────────────────────┬─────────┘
       │                        │                       │
┌──────▼─────────┐   ┌──────────▼─────────┐   ┌───────▼──────────┐
│  USER SERVICE  │   │  DIGEST SERVICE    │   │   CHAT SERVICE   │
│                │   │                    │   │                  │
│ • Auth         │   │ • Generation       │   │ • RAG Engine     │
│ • Preferences  │   │ • Scheduling       │   │ • LLM Interface  │
│ • Subscriptions│   │ • Personalization  │   │ • Context Mgmt   │
└────────┬───────┘   └─────────┬──────────┘   └────────┬─────────┘
         │                     │                       │
         │              ┌──────▼─────────┐            │
         │              │ CONTENT SERVICE│            │
         │              │                │            │
         │              │ • Aggregation  │            │
         │              │ • Deduplication│            │
         │              │ • Scoring      │            │
         │              └────────┬───────┘            │
         │                       │                    │
    ┌────▼───────────────────────▼────────────────────▼───┐
    │              DATA LAYER                              │
    ├─────────────┬─────────────┬─────────────┬───────────┤
    │ PostgreSQL  │   Redis     │  Vector DB  │  S3/Blob  │
    │ (Relational)│  (Cache)    │  (Pinecone/ │ (Archives)│
    │             │             │  Weaviate)  │           │
    └─────────────┴─────────────┴─────────────┴───────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
    ┌────▼───────┐   ┌──────▼────────┐   ┌────▼──────┐
    │  Scraper   │   │ External APIs │   │  LLM APIs │
    │   Workers  │   │ (RSS, GitHub, │   │ (Anthropic│
    │  (Celery)  │   │  News APIs)   │   │  OpenAI)  │
    └────────────┘   └───────────────┘   └───────────┘
```

### 1.2 Technology Stack

**Backend:**
- **API Framework**: FastAPI (Python 3.11+) - async support, automatic OpenAPI docs
- **Task Queue**: Celery + Redis - distributed task processing
- **Worker Orchestration**: Celery Beat - scheduled jobs for scraping
- **Database**: PostgreSQL 15+ - JSONB for flexible schemas
- **Cache**: Redis 7+ - session management, rate limiting, caching
- **Vector Store**: Pinecone or Weaviate - semantic search for RAG
- **Object Storage**: AWS S3 or Cloudflare R2 - raw article archives

**Frontend:**
- **Framework**: React 18 with TypeScript
- **State Management**: Zustand or React Query
- **UI Components**: Tailwind CSS + shadcn/ui
- **Build Tool**: Vite
- **Deployment**: Vercel or Cloudflare Pages

**LLM & AI:**
- **Primary LLM**: Claude 3.5 Sonnet (Anthropic) - summarization & chat
- **Fallback LLM**: GPT-4o (OpenAI) - redundancy
- **Embeddings**: voyage-3 or OpenAI text-embedding-3-large
- **RAG Framework**: LangChain or LlamaIndex

**Infrastructure:**
- **Hosting**: AWS (ECS Fargate for services, Lambda for light functions)
- **CDN**: Cloudflare - static assets, DDoS protection
- **Email**: AWS SES + Brevo/SendGrid for templating
- **Monitoring**: Sentry (errors), Datadog (metrics), PostHog (analytics)
- **CI/CD**: GitHub Actions
- **IaC**: Terraform or AWS CDK

**Development:**
- **Version Control**: GitHub (mono-repo structure)
- **Containerization**: Docker + Docker Compose for local dev
- **Testing**: pytest (backend), Vitest + React Testing Library (frontend)
- **Documentation**: OpenAPI/Swagger (auto-generated), Notion (internal)

---

## 2. Core Services Architecture

### 2.1 Content Aggregation Service

**Purpose**: Continuously fetch, parse, and store content from monitored sources

**Components:**

**A. Source Manager**
```python
# Pseudocode structure
class SourceManager:
    sources = [
        {
            "id": "openai_blog",
            "type": "rss",
            "url": "https://openai.com/blog/rss/",
            "check_frequency_hours": 2,
            "priority": "high",
            "companies": ["openai"]
        },
        {
            "id": "anthropic_github",
            "type": "github",
            "repo": "anthropic-ai/anthropic-sdk-python",
            "check_frequency_hours": 6,
            "events": ["release", "major_commit"],
            "companies": ["anthropic"]
        },
        # ... more sources
    ]
    
    def fetch_updates(self, source_config):
        """Fetch new content from a source"""
        
    def parse_content(self, raw_content, source_type):
        """Extract structured data from raw content"""
        
    def store_raw(self, content):
        """Store in S3 + metadata in PostgreSQL"""
```

**B. Deduplication Engine**
```python
class DeduplicationEngine:
    def calculate_similarity(self, article1, article2):
        """Use embedding cosine similarity + fuzzy string matching"""
        
    def find_duplicates(self, new_article):
        """Query vector DB for similar content (similarity > 0.85)"""
        
    def merge_duplicates(self, articles):
        """Combine metadata, choose canonical version"""
```

**C. Content Classifier**
```python
class ContentClassifier:
    def extract_entities(self, text):
        """Use LLM to extract: companies, people, products, technologies"""
        
    def assign_categories(self, article):
        """Multi-label: [industry, news_type, impact_level]"""
        
    def calculate_relevance_score(self, article, user_preferences):
        """Score 0-100 based on user's subscribed topics"""
```

**Data Model:**
```sql
CREATE TABLE articles (
    id UUID PRIMARY KEY,
    source_id VARCHAR(100),
    source_url TEXT UNIQUE,
    title TEXT NOT NULL,
    content TEXT,
    summary TEXT,
    published_at TIMESTAMP,
    fetched_at TIMESTAMP DEFAULT NOW(),
    embedding VECTOR(1536), -- for semantic search
    metadata JSONB, -- flexible schema for source-specific data
    companies TEXT[], -- array of company tags
    categories TEXT[],
    impact_score INTEGER, -- 1-10
    status VARCHAR(20) -- pending, processed, archived
);

CREATE INDEX idx_articles_published ON articles(published_at DESC);
CREATE INDEX idx_articles_companies ON articles USING GIN(companies);
CREATE INDEX idx_articles_embedding ON articles USING ivfflat(embedding);
```

**Scheduled Tasks:**
- High priority sources: Every 1-2 hours
- Medium priority: Every 6 hours
- Low priority: Daily
- Celery Beat schedule configuration

---

### 2.2 AI Summarization Service

**Purpose**: Generate high-quality summaries with fact-checking and contextualization

**Pipeline:**

**1. Summary Generation**
```python
async def generate_summary(article: Article, style: str = "standard"):
    prompt = f"""
    Summarize the following article for a technical professional.
    
    Source: {article.source_id}
    Title: {article.title}
    Content: {article.content[:4000]}
    
    Requirements:
    - 2-3 sentences (150-200 words)
    - Include key facts and numbers
    - Explain why this matters
    - Use accessible language (avoid excessive jargon)
    - If technical, include one example
    
    Article:
    {article.content}
    """
    
    summary = await claude_client.messages.create(
        model="claude-sonnet-4.5",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return summary.content[0].text
```

**2. Fact Extraction**
```python
def extract_key_facts(article_text, summary):
    """
    Use structured output from LLM to extract:
    - Key claims/announcements
    - Numerical data
    - Quotes
    - Dates/deadlines
    """
    
    prompt = """Extract structured facts:
    {
        "main_announcement": "",
        "key_numbers": [],
        "important_dates": [],
        "quotes": [],
        "related_entities": []
    }
    """
    # LLM returns JSON
```

**3. Cross-Validation**
```python
def cross_validate_claims(main_article, related_articles):
    """
    Find related articles from same time period
    Check if major claims are corroborated
    Flag uncorroborated claims for human review
    """
```

**Quality Metrics:**
- Factual accuracy (spot-checked by humans initially)
- Readability score (Flesch-Kincaid)
- User feedback (thumbs up/down)
- A/B test different prompts

---

### 2.3 Digest Generation Service

**Purpose**: Create personalized email digests for each user

**Algorithm:**

```python
class DigestGenerator:
    def generate_digest(self, user_id: str, date: datetime):
        """
        1. Get user preferences (companies, industries, delivery time)
        2. Fetch articles from last 24 hours matching preferences
        3. Score and rank articles
        4. Select top N articles (5-7 for free, 10-15 for pro)
        5. Generate personalized intro
        6. Render email template
        7. Queue for delivery
        """
        
        user = get_user(user_id)
        articles = self.get_relevant_articles(user, since=date - timedelta(days=1))
        ranked = self.rank_articles(articles, user)
        top_articles = ranked[:user.digest_size]
        
        email_html = self.render_email(
            user=user,
            articles=top_articles,
            intro=self.generate_intro(user, top_articles)
        )
        
        self.queue_email(user.email, email_html, scheduled_for=user.preferred_time)
```

**Ranking Algorithm:**
```python
def rank_articles(self, articles, user):
    """
    Scoring factors:
    1. Recency (log decay, recent = higher score)
    2. Source authority (official > news > community)
    3. Impact score (breaking news > routine updates)
    4. User preference match (primary topics > secondary)
    5. Engagement prediction (similar users clicked?)
    6. Diversity (avoid too many from one company)
    
    Final score = weighted sum of normalized factors
    """
    
    for article in articles:
        recency_score = calculate_recency(article.published_at)
        authority_score = SOURCE_WEIGHTS[article.source_id]
        impact_score = article.impact_score / 10
        preference_match = calculate_overlap(article.companies, user.subscriptions)
        predicted_ctr = ml_model.predict_ctr(article, user) # optional ML model
        
        article.score = (
            0.25 * recency_score +
            0.20 * authority_score +
            0.25 * impact_score +
            0.20 * preference_match +
            0.10 * predicted_ctr
        )
    
    # Apply diversity filter: max 3 articles per company
    return diversify_and_sort(articles)
```

**Email Template Structure:**
```html
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>/* Responsive CSS */</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Your UP2D8 Digest</h1>
            <p>{{ date }} | {{ user.name }}</p>
        </header>
        
        <section class="intro">
            <p>{{ personalized_intro }}</p>
        </section>
        
        {% for article in articles %}
        <article class="digest-item">
            <span class="badge">{{ article.category }}</span>
            <h2>{{ article.title }}</h2>
            <p class="summary">{{ article.summary }}</p>
            <div class="metadata">
                <span>{{ article.source_name }}</span> •
                <span>{{ article.published_at | human_readable }}</span>
            </div>
            <div class="actions">
                <a href="{{ article.url }}">Read Full Article</a>
                <a href="{{ chat_url }}?article_id={{ article.id }}">Ask AI</a>
            </div>
        </article>
        {% endfor %}
        
        <footer>
            <a href="{{ dashboard_url }}">View Dashboard</a>
            <a href="{{ preferences_url }}">Manage Preferences</a>
            <p class="unsubscribe">Not interested? <a href="{{ unsubscribe_url }}">Unsubscribe</a></p>
        </footer>
    </div>
</body>
</html>
```

**Delivery System:**
- Batch process users in cohorts based on timezone/preferred delivery time
- Use SES for sending, SQS for queuing
- Track opens (pixel), clicks (tracked links), bounces
- Retry logic for temporary failures
- Bounce/complaint handling (automatic unsub after threshold)

---

### 2.4 Conversational AI Service (RAG System)

**Purpose**: Answer user questions with context from digests + real-time search

**Architecture:**

```
┌───────────────────────────────────────────────────────────┐
│                    Chat Request                            │
│  "What did OpenAI announce this week?"                    │
└──────────────────────┬────────────────────────────────────┘
                       │
           ┌───────────▼────────────┐
           │  Query Understanding   │
           │  • Intent detection    │
           │  • Entity extraction   │
           │  • Temporal grounding  │
           └───────────┬────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼─────────┐        ┌──────────▼──────────┐
│  Retrieval Phase│        │  Real-time Search   │
│                 │        │  (if recent query)  │
│ 1. Vector       │        │                     │
│    Search       │        │  • Web search API   │
│                 │        │  • Direct scraping  │
│ 2. Metadata     │        └──────────┬──────────┘
│    Filter       │                   │
│                 │                   │
│ 3. Reranking    │                   │
└───────┬─────────┘                   │
        │                             │
        └──────────────┬──────────────┘
                       │
            ┌──────────▼─────────────┐
            │  Context Assembly      │
            │  • Top 5-10 articles   │
            │  • Conversation history│
            │  • User preferences    │
            └──────────┬─────────────┘
                       │
              ┌────────▼────────┐
              │  LLM Generation │
              │  (Claude/GPT)   │
              │  • Streaming    │
              │  • Citations    │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │  Response       │
              │  + Citations    │
              │  + Follow-up    │
              │    suggestions  │
              └─────────────────┘
```

**Implementation:**

```python
class RAGChatService:
    def __init__(self):
        self.vector_db = PineconeClient()
        self.llm = ClaudeClient()
        self.web_search = BraveSearchAPI()
        
    async def handle_query(self, user_id: str, query: str, session_id: str):
        # 1. Understand query intent
        intent = await self.classify_intent(query)
        entities = self.extract_entities(query)
        time_range = self.extract_time_range(query) # "this week", "yesterday", etc.
        
        # 2. Retrieve relevant context
        if intent == "recent_events":
            # Use vector search on recent articles
            articles = await self.vector_search(
                query_embedding=self.embed(query),
                filters={
                    "companies": entities["companies"],
                    "published_after": time_range.start,
                    "user_id": user_id  # only articles user has access to
                },
                top_k=10
            )
            
            # Optionally supplement with real-time web search
            if time_range.is_very_recent(hours=24):
                web_results = await self.web_search.search(query, recency="day")
                articles.extend(self.parse_web_results(web_results))
        
        elif intent == "explain_concept":
            # Search knowledge base + general web search
            articles = await self.vector_search(query, top_k=5)
            web_context = await self.web_search.search(f"{query} explained")
            articles.extend(self.parse_web_results(web_context))
        
        # 3. Rerank retrieved articles
        reranked = self.rerank(articles, query)
        top_articles = reranked[:5]
        
        # 4. Get conversation history
        chat_history = self.get_session_history(session_id, last_n=5)
        
        # 5. Assemble prompt
        context = self.format_context(top_articles)
        
        prompt = f"""You are an AI assistant helping a professional stay informed about technology companies and industries.

User Question: {query}

Relevant Articles:
{context}

Conversation History:
{chat_history}

Instructions:
- Answer based on the provided articles and your knowledge
- Cite sources using [Source Name] format
- If information is from articles older than 7 days, mention the date
- Be concise but thorough
- If you don't have enough information, say so and suggest what to search for

Answer:"""

        # 6. Stream response
        async for chunk in self.llm.stream(prompt):
            yield chunk
        
        # 7. Store interaction
        self.store_chat_message(session_id, query, response, articles_used=top_articles)
```

**Vector Search Optimization:**
```python
# Hybrid search: combine semantic + keyword
def hybrid_search(query: str, filters: dict, top_k: int = 10):
    # Semantic search (vector)
    semantic_results = vector_db.query(
        vector=embed(query),
        filter=filters,
        top_k=top_k * 2  # get more candidates
    )
    
    # Keyword search (BM25 on PostgreSQL)
    keyword_results = postgres.full_text_search(
        query=query,
        filters=filters,
        top_k=top_k * 2
    )
    
    # Combine and rerank using RRF (Reciprocal Rank Fusion)
    combined = reciprocal_rank_fusion(semantic_results, keyword_results)
    return combined[:top_k]
```

**Citation System:**
```python
def format_with_citations(response_text: str, sources: List[Article]):
    """
    Parse LLM response and add inline citations
    
    Example:
    "OpenAI released GPT-4.5 with improved reasoning [1]..."
    
    [1] OpenAI Blog - "Introducing GPT-4.5" (Oct 15, 2025)
    """
    
    # LLM outputs references like [1], [2]
    # Match with provided sources and format footer
    
    citation_footer = "\n\nSources:\n"
    for idx, source in enumerate(sources, 1):
        citation_footer += f"[{idx}] {source.source_name} - \"{source.title}\" ({source.published_at.strftime('%b %d, %Y')})\n"
        citation_footer += f"    {source.url}\n"
    
    return response_text + citation_footer
```

---

### 2.5 User Management Service

**Features:**
- Authentication (email/password + OAuth)
- Subscription management
- Preference storage
- Payment processing (Stripe integration)
- Usage tracking (rate limits, quotas)

**Data Models:**

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255), -- null if OAuth only
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    tier VARCHAR(20) DEFAULT 'free', -- free, pro, enterprise
    stripe_customer_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active' -- active, paused, cancelled
);

CREATE TABLE user_preferences (
    user_id UUID REFERENCES users(id),
    subscribed_companies TEXT[], -- ['openai', 'anthropic', 'google']
    subscribed_industries TEXT[], -- ['ai', 'semiconductors']
    digest_frequency VARCHAR(20) DEFAULT 'daily', -- daily, twice_daily, hourly
    delivery_time TIME DEFAULT '08:00:00',
    timezone VARCHAR(50) DEFAULT 'America/New_York',
    email_format VARCHAR(20) DEFAULT 'html', -- html, plaintext
    notification_preferences JSONB, -- {breaking_news: true, weekly_summary: false}
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE subscriptions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    stripe_subscription_id VARCHAR(100),
    plan VARCHAR(20), -- pro_monthly, pro_annual, enterprise
    status VARCHAR(20), -- active, past_due, canceled
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_activity (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    activity_type VARCHAR(50), -- email_open, email_click, chat_message, article_bookmark
    metadata JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_activity_user ON user_activity(user_id, timestamp DESC);
```

**API Endpoints:**

```python
# FastAPI router
@router.post("/auth/signup")
async def signup(email: str, password: str, name: str):
    """Create new user account"""
    
@router.post("/auth/login")
async def login(email: str, password: str):
    """Return JWT token"""
    
@router.get("/users/me")
async def get_current_user(token: str = Depends(verify_token)):
    """Get authenticated user profile"""
    
@router.put("/users/me/preferences")
async def update_preferences(prefs: UserPreferences, user: User = Depends(get_current_user)):
    """Update subscription and delivery preferences"""
    
@router.post("/subscriptions/upgrade")
async def upgrade_subscription(plan: str, user: User = Depends(get_current_user)):
    """Create Stripe checkout session for upgrade"""
    
@router.post("/webhooks/stripe")
async def handle_stripe_webhook(request: Request):
    """Handle Stripe events (payment success, subscription canceled, etc.)"""
```

---

## 3. Data Flow Diagrams

### 3.1 Content Pipeline Flow

```
[External Sources]
       │
       ├─→ [RSS Feeds] ──┐
       ├─→ [GitHub API] ─┤
       ├─→ [News APIs] ──┼─→ [Scraper Workers (Celery)]
       ├─→ [Web Scraping]┤         │
       └─→ [Social Media]┘         │
                                   │
                                   ▼
                         [Raw Content Storage]
                         (S3 + PostgreSQL metadata)
                                   │
                                   ▼
                      [Deduplication & Classification]
                         (Vector similarity + LLM)
                                   │
                                   ▼
                          [AI Summarization]
                          (Claude/GPT-4)
                                   │
                                   ▼
                      [Processed Articles Database]
                      (PostgreSQL + Vector embeddings)
```

### 3.2 Digest Delivery Flow

```
[Scheduled Time: 8 AM ET]
         │
         ▼
[Celery Beat Triggers Job]
         │
         ├─→ [Fetch Users with delivery_time = 8 AM]
         │
         ▼
[For each user in batch:]
    │
    ├─→ [Get user preferences]
    ├─→ [Query relevant articles (last 24h)]
    ├─→ [Rank & select top articles]
    ├─→ [Generate personalized intro (LLM)]
    ├─→ [Render email template]
    └─→ [Queue to SES via SQS]
                │
                ▼
         [AWS SES sends email]
                │
                ▼
       [Track delivery metrics]
```

### 3.3 Chat Interaction Flow

```
[User sends message in chat UI]
         │
         ▼
[WebSocket/SSE connection to API]
         │
         ▼
[Rate limit check] ─→ [403 if exceeded]
         │
         ▼
[Load session context]
    • Previous messages
    • User subscriptions
         │
         ▼
[Query understanding]
    • Extract entities
    • Determine intent
    • Temporal context
         │
         ├──────────┐
         │          │
         ▼          ▼
[Vector Search] [Web Search]
    articles      (if recent)
         │          │
         └────┬─────┘
              │
              ▼
     [Assemble context]
     • Top 5 articles
     • Chat history
     • User context
              │
              ▼
      [LLM Generation]
      (stream response)
              │
              ▼
     [Format with citations]
              │
              ▼
     [Stream to client]
     [Store in session]
```

---

## 4. Scalability Considerations

### 4.1 Expected Load (Year 1)

- **Users**: 100K registered, 60K monthly active
- **Emails**: 60K/day = 21.9M/year
- **API Requests**: ~500 req/sec peak (dashboard + chat)
- **Articles Processed**: ~10K new articles/day
- **Chat Messages**: ~50K/day
- **Database Size**: ~500 GB (articles + embeddings)

### 4.2 Scaling Strategy

**Horizontal Scaling:**
- API servers: Auto-scale based on CPU/memory (ECS Fargate)
- Worker pool: Scale Celery workers based on queue length
- Database: Read replicas for queries, connection pooling

**Caching Strategy:**
- **Redis L1 Cache**: User sessions, rate limits (TTL: 1 hour)
- **Redis L2 Cache**: Frequently accessed articles (TTL: 24 hours)
- **CDN**: Static assets, rendered email templates
- **Database query cache**: Materialized views for dashboards

**Database Optimization:**
- Partition articles table by published_date (monthly partitions)
- Archive articles older than 1 year to cold storage
- Index optimization based on query patterns
- Connection pooling (PgBouncer)

**Cost Optimization:**
- Use spot instances for non-critical batch jobs
- Compress archives in S3 with Intelligent-Tiering
- Cache LLM responses for common queries (semantic dedup)
- Batch API calls to LLM providers
- Monitor and alert on unusual API usage spikes

### 4.3 Disaster Recovery

- **Database**: Daily backups, point-in-time recovery (PITR)
- **RTO (Recovery Time Objective)**: 1 hour for critical services
- **RPO (Recovery Point Objective)**: 15 minutes of data loss acceptable
- **Multi-region**: Passive secondary region (future)
- **Data replication**: S3 cross-region replication for archives

---

## 5. Security Architecture

### 5.1 Authentication & Authorization

**Authentication:**
- JWT tokens (access token: 15 min, refresh token: 7 days)
- OAuth 2.0 with Google/GitHub
- Password requirements: min 12 chars, complexity enforced
- 2FA optional (TOTP-based, for sensitive accounts)

**Authorization:**
- Role-based access control (RBAC): user, admin, enterprise_admin
- API key-based auth for Enterprise tier programmatic access
- Scoped permissions: read:articles, write:preferences, manage:team

**Rate Limiting:**
```python
rate_limits = {
    "free": {
        "api_requests": "100/hour",
        "chat_messages": "10/day",
        "digest_deliveries": "1/day"
    },
    "pro": {
        "api_requests": "1000/hour",
        "chat_messages": "500/day",
        "digest_deliveries": "24/day"
    },
    "enterprise": {
        "api_requests": "10000/hour",
        "chat_messages": "unlimited",
        "digest_deliveries": "unlimited"
    }
}
```

### 5.2 Data Protection

**Encryption:**
- At rest: AES-256 for database and S3
- In transit: TLS 1.3 for all communications
- Secrets management: AWS Secrets Manager or HashiCorp Vault

**PII Handling:**
- User emails encrypted in database
- Payment info never stored (Stripe handles)
- Anonymize analytics data (hash user IDs)
- GDPR compliance: data export and deletion endpoints

**Input Validation:**
- Sanitize all user inputs (prevent XSS, SQL injection)
- File upload restrictions (type, size)
- Content Security Policy (CSP) headers

---

## 6. Monitoring & Observability

### 6.1 Metrics to Track

**System Health:**
- API response times (p50, p95, p99)
- Error rates by endpoint
- Database query performance
- Queue lengths (Celery, SQS)
- Cache hit rates

**Business Metrics:**
- Daily/monthly active users
- Email open and click rates
- Chat engagement (messages per user)
- Conversion funnel (signup → activation → paid)
- Churn rate

**Cost Metrics:**
- LLM API costs per user
- Infrastructure costs per user
- Email delivery costs

### 6.2 Alerting

**Critical Alerts (PagerDuty):**
- Service downtime (API, database)
- Error rate spike (>5% requests failing)
- Email delivery failure rate >10%
- Payment processing failures

**Warning Alerts (Slack):**
- High API latency (>2s p95)
- LLM API quota approaching limit
- Disk space >80%
- Abnormal traffic patterns

### 6.3 Logging

**Structured Logging:**
```json
{
    "timestamp": "2025-10-23T14:32:11Z",
    "level": "INFO",
    "service": "digest-service",
    "user_id": "uuid",
    "action": "digest_generated",
    "metadata": {
        "articles_included": 7,
        "processing_time_ms": 450,
        "llm_tokens_used": 1200
    }
}
```

**Log Aggregation**: CloudWatch Logs or ELK stack
**Retention**: 30 days hot, 1 year cold storage

---

## 7. Development Workflow

### 7.1 Repository Structure

```
up2d8/
├── backend/
│   ├── api/              # FastAPI application
│   │   ├── routers/      # API endpoint definitions
│   │   ├── models/       # Pydantic models
│   │   ├── services/     # Business logic
│   │   └── utils/
│   ├── workers/          # Celery tasks
│   ├── scripts/          # One-off utilities
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── api/
│   ├── public/
│   └── package.json
├── infrastructure/       # Terraform/CDK
├── docker/
│   ├── Dockerfile.api
│   ├── Dockerfile.worker
│   └── docker-compose.yml
├── docs/
└── README.md
```

### 7.2 CI/CD Pipeline

**GitHub Actions Workflow:**
1. **On PR**: Run tests, linters, type checks
2. **On merge to main**: Deploy to staging
3. **Manual approval**: Promote to production
4. **Rollback**: One-click revert to previous version

**Deployment Strategy:**
- Blue-green deployments for zero downtime
- Canary releases for risky changes (5% → 25% → 100%)
- Feature flags for gradual rollouts

---

## 8. Open Technical Questions

1. **LLM Provider Mix**: Should we use multiple providers (Claude + GPT-4) for redundancy/cost optimization?
2. **Vector DB Choice**: Pinecone (managed) vs. Weaviate (self-hosted) vs. pgvector (PostgreSQL extension)?
3. **Real-time Updates**: WebSocket vs. Server-Sent Events for chat streaming?
4. **Search Engine**: Build custom or integrate existing (Algolia, Elasticsearch)?
5. **Email Service**: AWS SES alone, or add SendGrid/Postmark for better analytics?
6. **Monitoring Stack**: Datadog vs. self-hosted (Prometheus/Grafana)?

---

## Next Steps

1. **Prototype Core Pipeline**: Build MVP scraper → summarizer → digest generator
2. **Set Up Infrastructure**: Provision AWS resources, configure CI/CD
3. **Implement Auth & User Management**: Basic signup/login flow
4. **Build Frontend**: Email template + simple dashboard
5. **Alpha Test**: Internal team testing with real data sources
6. **Beta Launch**: Invite 50-100 external users

---

**Document Status**: Ready for Implementation Planning  
**Next Review**: After MVP completion  
**Contact**: engineering@up2d8.ai
