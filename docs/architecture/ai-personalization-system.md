# AI-Powered Personalization System Architecture

**Date**: October 24, 2025
**Status**: Design Document
**Goal**: Build a scalable, learning personalization system that improves email digest quality over time

---

## Executive Summary

We're designing a **hybrid personalization system** that combines:
1. **Explicit preferences** (user-selected companies, industries)
2. **Implicit behavioral signals** (clicks, reads, time spent)
3. **AI-powered relevance scoring** (semantic similarity, topic modeling)
4. **Continuous learning** (feedback loops that improve recommendations)

**Key Principle**: Start simple with rule-based ranking, progressively enhance with ML as we gather data.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERSONALIZATION PIPELINE                      │
└─────────────────────────────────────────────────────────────────┘

 User Preferences          Behavioral Signals        AI/ML Layer
┌──────────────┐          ┌───────────────┐        ┌──────────────┐
│ Subscriptions│          │ Email Opens   │        │ Embeddings   │
│ Companies    │───┐      │ Link Clicks   │───┐    │ Similarity   │
│ Industries   │   │      │ Read Time     │   │    │ Scoring      │
│ Topics       │   │      │ Bookmarks     │   │    │ Topic Models │
└──────────────┘   │      │ Thumbs Up/Down│   │    └──────────────┘
                   │      └───────────────┘   │           │
                   │              │            │           │
                   └──────────────┼────────────┴───────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │   SCORING ALGORITHM     │
                    │  (Weighted Combination) │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │   RANKED ARTICLES       │
                    │   (Top N for Digest)    │
                    └─────────────────────────┘
```

---

## Phase 1: Foundation (MVP - Week 6) ✅ CURRENT

### What We Have Now

**Explicit Preferences**:
- User can subscribe to companies, industries, technologies, people
- Simple array overlap filtering (PostgreSQL `&&` operator)
- Binary match: article either matches subscription or doesn't

**Current Limitations**:
- No ranking beyond recency
- No learning from user behavior
- No relevance scoring
- No feedback mechanism
- All articles with matching companies are treated equally

### What We're Building Next

**Short-term improvements** (this session):
1. ✅ Add feedback mechanism (thumbs up/down on articles)
2. ✅ Implement relevance scoring algorithm
3. ✅ Track user engagement signals
4. ✅ Build learning loop infrastructure

---

## Phase 2: Intelligent Scoring (Week 6-7) 🎯 NEXT

### Goal
Rank articles by relevance, not just filter them. Learn from user behavior.

### Components

#### 1. **Article Relevance Score**

A weighted score combining multiple signals:

```python
relevance_score = (
    0.30 * preference_match_score +    # Matches user's explicit subscriptions
    0.25 * engagement_score +          # Historical engagement with similar content
    0.20 * recency_score +             # How recent the article is
    0.15 * quality_score +             # Article quality (existing field)
    0.10 * diversity_score             # Avoid echo chamber
)
```

**Breakdown**:

**Preference Match Score** (0-100):
- Exact company match: 100 points
- Related industry match: 75 points
- Technology/topic match: 50 points
- Partial match (mentioned in content): 25 points

**Engagement Score** (0-100):
- Based on user's past behavior with similar articles
- Clicks on similar companies: +30
- Time spent reading similar topics: +25
- Bookmarks on related content: +20
- Thumbs up on similar articles: +25

**Recency Score** (0-100):
- Last 6 hours: 100 points
- 6-12 hours: 80 points
- 12-18 hours: 60 points
- 18-24 hours: 40 points
- Older: decay exponentially

**Quality Score** (0-100):
- Already stored in database
- Based on source authority, content quality

**Diversity Score** (0-100):
- Penalize if too many articles from same company
- Reward if introduces new topics
- Prevents echo chamber

#### 2. **User Engagement Tracking**

**Database Tables** (already exist):

```python
# EmailEvent - tracks email interactions
- event_type: "opened", "clicked", "bounced"
- article_id: which article was clicked
- timestamp: when

# Bookmark - saved articles
- user_id, article_id
- created_at

# UserActivity - general activity tracking
- activity_type: "read", "share", "thumbs_up", "thumbs_down"
- article_id
- metadata: {"read_time_seconds": 45}
```

**New Table Needed**: `ArticleFeedback`

```sql
CREATE TABLE article_feedback (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    article_id UUID REFERENCES articles(id),
    digest_id UUID REFERENCES digests(id),

    -- Feedback type
    feedback_type VARCHAR(20), -- 'thumbs_up', 'thumbs_down', 'not_relevant'

    -- Optional text feedback
    feedback_text TEXT,

    -- Context
    feedback_source VARCHAR(20), -- 'email', 'web', 'api'

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id, article_id, digest_id)
);
```

#### 3. **Feedback Loop**

**In Email Template**:
```html
<!-- Add to each article card -->
<div class="article-feedback">
    <a href="https://up2d8.ai/feedback/thumbs-up?article_id={id}&digest_id={digest_id}&user_id={user_id}">
        👍 Helpful
    </a>
    <a href="https://up2d8.ai/feedback/thumbs-down?article_id={id}&digest_id={digest_id}&user_id={user_id}">
        👎 Not relevant
    </a>
</div>
```

**API Endpoint**:
```python
POST /api/v1/feedback
{
    "article_id": "uuid",
    "digest_id": "uuid",
    "feedback_type": "thumbs_up" | "thumbs_down",
    "feedback_text": "optional comment"
}
```

**Learning Algorithm**:
```python
def update_user_preferences_from_feedback(user_id, article_id, feedback_type):
    """
    When user gives thumbs up/down, extract signals and update preferences.
    """
    article = get_article(article_id)

    if feedback_type == "thumbs_up":
        # Boost preference for article's companies/industries
        for company in article.companies:
            increment_interest(user_id, "company", company, weight=+0.1)
        for industry in article.industries:
            increment_interest(user_id, "industry", industry, weight=+0.05)

    elif feedback_type == "thumbs_down":
        # Reduce preference
        for company in article.companies:
            increment_interest(user_id, "company", company, weight=-0.1)
```

---

## Phase 3: AI/ML Enhancement (Week 10-11 + Future)

### Semantic Similarity (Embeddings)

**Goal**: Find articles similar to what user likes, even if not explicitly subscribed.

**Approach**:
1. **Generate embeddings** for all articles (already have embedding infrastructure)
2. **Store user preference vector** - weighted average of articles they liked
3. **Cosine similarity** - rank new articles by similarity to user's preference vector

```python
# User Preference Vector
user_vector = weighted_average([
    article.embedding for article in user_thumbs_up_articles
])

# Score new articles
for article in new_articles:
    similarity_score = cosine_similarity(user_vector, article.embedding)
    article.ai_relevance_score = similarity_score
```

**Implementation**:
- Week 10: Set up vector DB (already have ChromaDB)
- Week 10: Generate embeddings for articles (already doing this)
- Week 11: Build user preference vectors
- Week 11: Add semantic similarity to scoring algorithm

### Topic Modeling

**Goal**: Discover hidden topics user cares about.

**Approach**:
- Use LDA or BERTopic to extract topics from user's liked articles
- Find new articles matching those topics
- Surface new companies/industries user might like

**Future**: Fine-tune LLM on user behavior for personalized summarization.

---

## Phase 4: Advanced Personalization (Month 4-6+)

### Collaborative Filtering

"Users who liked X also liked Y"

```python
# Find similar users
similar_users = find_users_with_similar_preferences(user_id, limit=50)

# Get articles they liked that current user hasn't seen
recommended_articles = get_liked_articles(similar_users) - user_seen_articles
```

### Reinforcement Learning

Model digest generation as a **Multi-Armed Bandit** problem:
- Each article is an "arm"
- "Reward" = user engagement (click, read time, thumbs up)
- Algorithm learns which types of articles to show

**Algorithms**:
- Start with **Epsilon-Greedy**: 90% exploit (show best), 10% explore (try new)
- Upgrade to **Thompson Sampling** or **UCB** for better exploration

### Personalized Summarization

Fine-tune LLM to generate summaries matching user's reading level and interests.

```python
# Different users, different summaries
user_technical_level = infer_from_engagement()

if user_technical_level == "expert":
    summary = generate_technical_summary(article)
else:
    summary = generate_accessible_summary(article)
```

---

## Data Storage Strategy

### User Preference Profile (New Table)

```sql
CREATE TABLE user_preference_profile (
    user_id UUID PRIMARY KEY REFERENCES users(id),

    -- Learned interest weights (JSONB for flexibility)
    company_weights JSONB DEFAULT '{}',
    -- {"OpenAI": 0.85, "Anthropic": 0.72, "Google": 0.45}

    industry_weights JSONB DEFAULT '{}',
    -- {"AI": 0.90, "Cloud Computing": 0.60}

    topic_weights JSONB DEFAULT '{}',
    -- {"LLMs": 0.95, "GPUs": 0.70, "Ethics": 0.40}

    -- Embedding vector (for semantic search)
    preference_embedding VECTOR(384), -- if using pgvector

    -- Metrics
    total_feedback_count INT DEFAULT 0,
    positive_feedback_count INT DEFAULT 0,
    avg_engagement_score DECIMAL(5,2),

    -- Timestamps
    last_updated_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Engagement Metrics (Per User)

```sql
CREATE TABLE user_engagement_metrics (
    user_id UUID PRIMARY KEY REFERENCES users(id),

    -- Email metrics
    total_emails_sent INT DEFAULT 0,
    total_emails_opened INT DEFAULT 0,
    total_links_clicked INT DEFAULT 0,
    avg_articles_clicked_per_digest DECIMAL(5,2),

    -- Engagement rates
    open_rate DECIMAL(5,4),  -- e.g., 0.6500 = 65%
    click_rate DECIMAL(5,4),
    engagement_score DECIMAL(5,2), -- composite score

    -- Time-based
    avg_time_to_open_seconds INT,
    avg_read_time_seconds INT,

    -- Preferences
    preferred_reading_time TIME, -- when they usually open emails

    -- Last calculated
    last_calculated_at TIMESTAMP DEFAULT NOW()
);
```

---

## Implementation Plan

### Week 6-7: Foundation (THIS SESSION)

1. **Create `article_feedback` table**
2. **Create `user_preference_profile` table**
3. **Add feedback API endpoints**
4. **Implement basic relevance scoring algorithm**
5. **Update email template with feedback buttons**
6. **Build feedback tracking system**

### Week 7-8: Behavioral Learning

1. **Track email opens and clicks properly**
2. **Calculate engagement metrics per user**
3. **Update relevance scores based on behavior**
4. **Build admin dashboard to view metrics**

### Week 10-11: AI Enhancement

1. **Generate user preference embeddings**
2. **Add semantic similarity to ranking**
3. **Implement topic modeling**
4. **A/B test AI recommendations vs rule-based**

### Month 4+: Advanced Features

1. **Collaborative filtering**
2. **Reinforcement learning for article selection**
3. **Personalized summarization**
4. **Predictive engagement models**

---

## Success Metrics

### Short-term (Week 6-8)

- ✅ Feedback collection rate: >5% of digest recipients provide feedback
- ✅ Article relevance score variance: users see different top articles based on preferences
- ✅ Engagement improvement: +10% click-through rate vs baseline

### Medium-term (Week 10-12)

- ✅ AI relevance accuracy: thumbs up rate >70% on AI-recommended articles
- ✅ Diversity score: <50% overlap in articles across different user groups
- ✅ Open rate: >65% (industry benchmark: 40-50%)

### Long-term (Month 4-6)

- ✅ Predictive accuracy: can predict which articles user will click with >60% accuracy
- ✅ Retention: <5% unsubscribe rate monthly
- ✅ NPS (Net Promoter Score): >50

---

## Privacy & Ethics

### Data Collection

**We collect**:
- Article clicks
- Reading time (approximate)
- Thumbs up/down feedback
- Subscriptions and preferences

**We DON'T collect**:
- Email forwarding behavior
- Clipboard activity
- Other browsing behavior outside UP2D8

### User Control

Users can:
- ✅ See what data we've collected (GDPR compliance)
- ✅ Export their data
- ✅ Delete their data
- ✅ Opt out of personalization (get chronological feed instead)

### Transparency

- Explain in settings: "We use your feedback to improve recommendations"
- Show "Why this article?" explanations
- Let users adjust personalization strength (low/medium/high)

---

## Technical Implementation Notes

### Caching Strategy

```python
# Cache user preference profiles (Redis)
@cache(ttl=3600)  # 1 hour
def get_user_preference_profile(user_id):
    return db.query(UserPreferenceProfile).filter_by(user_id=user_id).first()

# Invalidate cache on feedback
def record_feedback(user_id, article_id, feedback_type):
    save_feedback(user_id, article_id, feedback_type)
    cache.delete(f"user_preference_profile:{user_id}")
```

### Batch Processing

```python
# Update preference profiles nightly
@celery_app.task
def update_all_user_preference_profiles():
    """
    Runs nightly to recalculate all user preference weights
    based on last 30 days of behavior.
    """
    users = User.query.filter(User.status == "active").all()
    for user in users:
        calculate_and_save_preference_profile.delay(user.id)
```

### A/B Testing Framework

```python
def get_article_ranking_algorithm(user_id):
    """
    Assign users to test groups for A/B testing different algorithms.
    """
    user_hash = hash(user_id)

    if user_hash % 100 < 10:  # 10% of users
        return "collaborative_filtering"
    elif user_hash % 100 < 20:  # 10% of users
        return "semantic_similarity"
    else:  # 80% of users
        return "weighted_scoring"  # default
```

---

## Cost Considerations

### Free Tier (MVP)

- **Embeddings**: Use sentence-transformers (FREE)
- **Vector DB**: ChromaDB (FREE)
- **LLM**: Ollama for local testing (FREE)

### Production (Paid)

- **Embeddings**: Voyage AI ($0.12 per 1M tokens) or OpenAI ($0.13 per 1M tokens)
- **Vector DB**: Pinecone ($70/month for 100k vectors)
- **LLM**: Claude API for high-quality summarization (~$0.05 per article)

**Estimated costs at scale**:
- 1000 users, 10 articles/day = 10k embeddings/day = $36/month
- Vector DB: $70/month
- LLM summarization: $500/month (10k articles)

**Total**: ~$600/month for 1000 users = $0.60 per user/month

---

## Next Steps

**This Session** (implement foundation):
1. Create database migrations for feedback tables
2. Add feedback API endpoints
3. Implement basic relevance scoring
4. Update email template with feedback buttons
5. Build feedback processing pipeline

**Week 7**:
1. Deploy feedback system to production
2. Collect 2 weeks of feedback data
3. Build admin dashboard to visualize engagement

**Week 8-9**:
1. Analyze feedback patterns
2. Tune scoring algorithm weights
3. Measure impact on engagement metrics

---

**Document Version**: 1.0
**Last Updated**: 2025-10-24
**Status**: Ready for Implementation
