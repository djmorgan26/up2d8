# UP2D8 Analytics System

## Overview

The UP2D8 Analytics System is a comprehensive data tracking and insights platform that helps you understand:

- **Source Performance**: Which content sources users engage with most
- **Company Popularity**: Which companies/startups users care about
- **Industry Trends**: Which industries get the most positive feedback
- **Content Quality**: Article-level engagement and feedback patterns
- **User Segments**: Understanding different user preference clusters

This system is designed to **scale with your customer base** and provide actionable insights to optimize content curation and personalization.

## Database Schema

### 1. Source Analytics (`source_analytics`)

Tracks aggregate metrics per content source:

```sql
- source_id (PK, FK to sources)
- total_articles_delivered
- total_positive_feedback
- total_negative_feedback
- total_clicks
- avg_relevance_score
- engagement_rate  # (positive + clicks) / delivered
- last_updated
```

**Use Case**: Identify which sources (TechCrunch AI, Anthropic Blog, etc.) users love vs. sources that should be deprioritized.

### 2. Company Analytics (`company_analytics`)

Tracks user engagement with content about specific companies:

```sql
- company_name (PK)
- total_mentions
- total_positive_feedback
- total_negative_feedback
- total_users_interested
- sentiment_score  # positive / (positive + negative)
- popularity_score  # weighted: (positive * 2) - negative
- last_updated
```

**Use Case**: Discover trending companies, identify companies users want more/less content about.

**Example Query**:
```sql
SELECT company_name, popularity_score, sentiment_score
FROM company_analytics
ORDER BY popularity_score DESC
LIMIT 10;
```

### 3. Industry Analytics (`industry_analytics`)

Tracks user engagement with different industry topics:

```sql
- industry_name (PK)
- total_mentions
- total_positive_feedback
- total_negative_feedback
- total_users_interested
- sentiment_score
- popularity_score
- last_updated
```

**Use Case**: Understand which industries resonate with your audience (AI, fintech, healthcare, etc.).

### 4. Article Analytics (`article_analytics`)

Tracks performance of individual articles:

```sql
- article_id (PK, FK to articles)
- times_delivered
- unique_users_delivered
- positive_feedback_count
- negative_feedback_count
- click_count
- avg_relevance_score
- engagement_rate  # (positive + clicks) / delivered
- last_updated
```

**Use Case**: A/B test different article types, identify high-quality vs. low-quality content patterns.

### 5. Daily Analytics (`daily_analytics`)

Time-series data for growth tracking:

```sql
- date (PK)
- total_digests_sent
- total_articles_delivered
- total_feedback_received
- total_positive_feedback
- total_negative_feedback
- total_clicks
- active_users
- avg_relevance_score
- overall_engagement_rate
- created_at
```

**Use Case**: Track daily growth, identify trends over time, measure engagement improvements.

### 6. User Cohort Analytics (`user_cohort_analytics`)

Track user segments for personalization insights:

```sql
- cohort_name (PK)
- cohort_definition (JSON)  # Criteria for this cohort
- total_users
- avg_feedback_count
- avg_engagement_rate
- top_companies (JSON array)
- top_industries (JSON array)
- top_sources (JSON array)
- last_updated
```

**Use Case**: Compare preferences between user segments (e.g., "AI Engineers" vs. "Product Managers").

## API Endpoints

All analytics endpoints require authentication and are accessible at `/api/v1/analytics/*`.

### 1. GET `/api/v1/analytics/companies/top`

Get top companies by user engagement.

**Query Parameters**:
- `limit` (integer, default=10): Number of results (1-100)

**Response**:
```json
[
  {
    "company": "anthropic",
    "positive_feedback": 45,
    "negative_feedback": 3,
    "sentiment_score": 0.94,
    "popularity_score": 87.0
  },
  ...
]
```

### 2. GET `/api/v1/analytics/industries/top`

Get top industries by user engagement.

**Query Parameters**:
- `limit` (integer, default=10)

**Response**:
```json
[
  {
    "industry": "ai",
    "positive_feedback": 120,
    "negative_feedback": 8,
    "sentiment_score": 0.94,
    "popularity_score": 232.0
  },
  ...
]
```

### 3. GET `/api/v1/analytics/sources/performance`

Get performance metrics for all content sources.

**Response**:
```json
[
  {
    "source_name": "TechCrunch AI",
    "articles_delivered": 450,
    "positive_feedback": 89,
    "negative_feedback": 12,
    "engagement_rate": 0.2244
  },
  ...
]
```

### 4. GET `/api/v1/analytics/daily/stats`

Get daily aggregated statistics.

**Query Parameters**:
- `days` (integer, default=7): Number of days to fetch (1-90)

**Response**:
```json
[
  {
    "date": "2025-10-25",
    "digests_sent": 150,
    "articles_delivered": 1500,
    "feedback_received": 320,
    "positive_feedback": 280,
    "negative_feedback": 40,
    "active_users": 150
  },
  ...
]
```

### 5. GET `/api/v1/analytics/summary`

Get a comprehensive dashboard summary.

**Response**:
```json
{
  "top_companies": [...],
  "top_industries": [...],
  "source_performance": [...],
  "daily_stats": [...],
  "generated_at": "2025-10-25T16:30:00"
}
```

## How Analytics Are Tracked

### Automatic Tracking Points

1. **When Article Delivered in Digest**
   - `track_article_delivered(article_id, user_id, relevance_score)`
   - Updates: `article_analytics`, `source_analytics`, `daily_analytics`

2. **When User Gives Feedback** (👍/👎)
   - `track_feedback(article_id, user_id, feedback_type)`
   - Updates: `article_analytics`, `source_analytics`, `company_analytics`, `industry_analytics`, `daily_analytics`

3. **When Digest Sent**
   - `track_digest_sent(user_id, article_count)`
   - Updates: `daily_analytics`

### Integration Example

In your feedback endpoint (`/api/v1/feedback/track`):

```python
# After saving feedback to database
analytics_tracker = get_analytics_tracker(db)
analytics_tracker.track_feedback(article_id, user_id, feedback_type)
```

## Business Insights You Can Extract

### 1. Content Strategy Optimization

**Question**: "Which sources should we prioritize?"

```python
GET /api/v1/analytics/sources/performance
```

Look for sources with high `engagement_rate`. Prioritize high-performing sources in relevance scoring.

### 2. Company Focus

**Question**: "Which companies are users most interested in?"

```python
GET /api/v1/analytics/companies/top?limit=20
```

Use `popularity_score` to identify trending companies. Add high-scoring companies to scraped sources.

### 3. Industry Trends

**Question**: "Are users more interested in AI or fintech content?"

```python
GET /api/v1/analytics/industries/top
```

Compare `sentiment_score` and `popularity_score` across industries.

### 4. Growth Tracking

**Question**: "Is engagement improving over time?"

```python
GET /api/v1/analytics/daily/stats?days=30
```

Track `overall_engagement_rate` trend over 30 days.

### 5. Content Quality

**Question**: "What types of articles perform best?"

Query `article_analytics` directly:

```sql
SELECT a.title, a.author, aa.engagement_rate, aa.positive_feedback_count
FROM article_analytics aa
JOIN articles a ON aa.article_id = a.id
WHERE aa.times_delivered > 10
ORDER BY aa.engagement_rate DESC
LIMIT 20;
```

Analyze patterns in high-performing articles (author, source type, topic, length, etc.).

## Scaling Considerations

### Current Design (MVP)

- ✅ Real-time tracking on feedback events
- ✅ Efficient upserts with `ON CONFLICT` clauses
- ✅ Indexed popularity scores for fast queries
- ✅ Works for 1-10,000 users

### Future Optimizations (10,000+ users)

1. **Batch Processing**
   - Move to async background jobs for analytics updates
   - Use Celery tasks to aggregate analytics hourly instead of real-time

2. **Materialized Views**
   - Create PostgreSQL materialized views for complex aggregations
   - Refresh views daily instead of computing on-demand

3. **Time-Series Database**
   - Move `daily_analytics` to TimescaleDB for better time-series performance
   - Enable efficient time-based queries and downsampling

4. **Caching Layer**
   - Cache analytics API responses in Redis (TTL: 1 hour)
   - Invalidate cache when significant updates occur

5. **Data Warehouse**
   - Export to BigQuery/Snowflake for advanced analytics
   - Build custom dashboards with Looker/Tableau

## Testing the System

### 1. Test Feedback Tracking

```bash
# Give feedback on an article
curl -X GET "http://localhost:8000/api/v1/feedback/track?article_id=<ARTICLE_ID>&user_id=<USER_ID>&type=thumbs_up"

# Check company_analytics was updated
docker-compose exec -T postgres psql -U up2d8 -d up2d8 -c "SELECT * FROM company_analytics;"
```

### 2. Test Analytics API

```bash
# Get top companies
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  http://localhost:8000/api/v1/analytics/companies/top

# Get analytics summary
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  http://localhost:8000/api/v1/analytics/summary
```

### 3. Verify Daily Aggregation

```bash
# Check daily_analytics table
docker-compose exec -T postgres psql -U up2d8 -d up2d8 -c \
  "SELECT date, total_digests_sent, total_feedback_received FROM daily_analytics ORDER BY date DESC LIMIT 7;"
```

## Next Steps

1. **Build Admin Dashboard** (Week 9-10)
   - Create React dashboard to visualize analytics
   - Show top companies, industries, source performance
   - Display engagement trends over time

2. **Implement Cohort Analysis** (Week 11)
   - Define user cohorts (power users, casual users, industry-specific)
   - Track cohort-specific preferences
   - A/B test content strategies per cohort

3. **Advanced Personalization** (Week 12+)
   - Use analytics to weight relevance scoring
   - Boost articles from high-performing sources
   - Prioritize popular companies/industries globally

4. **Predictive Analytics** (Future)
   - ML models to predict article engagement before sending
   - Churn prediction based on declining engagement
   - Recommend new sources/companies based on trends

## File Locations

- **Migration**: `backend/api/db/migrations/versions/85b0e7797f6d_add_analytics_tracking_tables.py`
- **Service**: `backend/api/services/analytics_tracker.py`
- **API Routes**: `backend/api/routers/analytics.py`
- **Integration**: `backend/api/routers/feedback.py` (lines 132-133)

## Summary

The UP2D8 Analytics System provides comprehensive tracking of user behavior, content performance, and engagement patterns. It's designed to:

✅ **Track everything**: Sources, companies, industries, articles, daily trends
✅ **Scale gracefully**: Efficient queries, indexed lookups, ready for optimization
✅ **Actionable insights**: API endpoints to query any metric you need
✅ **Future-proof**: Foundation for advanced analytics, ML, and personalization

Use this system to understand your users, optimize content curation, and grow engagement as your platform scales! 🚀
