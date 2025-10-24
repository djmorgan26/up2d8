# Content Scraping System - Feature Documentation

## Overview

The UP2D8 content scraping system automatically fetches articles from multiple sources including RSS feeds, web pages, GitHub releases, and APIs. The system runs as background tasks using Celery, stores articles in PostgreSQL, and handles deduplication.

**Status**: ✅ Implemented (Week 3)
**Created**: 2025-10-24
**Last Updated**: 2025-10-24

---

## Architecture

### Components

1. **Source Configuration** (`backend/config/sources.yaml`)
   - Centralized YAML file defining all content sources
   - Includes 14 sources: OpenAI, Anthropic, Google, Microsoft, NVIDIA, etc.
   - Configuration includes: URL, type, priority, check interval, companies, industries

2. **Scraper Service** (`backend/api/services/scraper.py`)
   - Base scraper class with retry logic and error handling
   - RSS/Atom feed scraper using `feedparser`
   - Web scraper using Playwright for JavaScript-rendered pages
   - GitHub scraper for releases and commits
   - Factory pattern for creating appropriate scraper instances

3. **Celery Workers** (`backend/workers/`)
   - Celery app configuration with Redis broker
   - Scraping tasks: single source, batch by priority, all sources
   - Scheduled tasks via Celery Beat
   - Task queues for prioritization

4. **API Endpoints** (`backend/api/routers/scraping.py`)
   - Source management endpoints
   - Manual scraping triggers
   - Article listing and statistics
   - Task status monitoring

5. **Database Models** (`backend/api/db/models.py`)
   - `Source` table: Source configurations and health metrics
   - `Article` table: Scraped content with metadata
   - Content hashing for deduplication

---

## Configuration

### Source Configuration Format

```yaml
- id: openai_blog
  name: OpenAI Blog
  type: rss  # rss, scrape, github, api
  url: https://openai.com/blog/rss/
  check_interval_hours: 2
  priority: high  # high, medium, low
  authority_score: 95
  companies: [openai]
  industries: [ai, machine_learning]
  active: true
```

### Supported Source Types

1. **RSS Feeds**:
   - Automatic parsing of RSS/Atom feeds
   - Extracts: title, content, author, published date
   - Examples: OpenAI Blog, Anthropic News, Google AI Blog

2. **Web Scraping**:
   - Uses Playwright for JavaScript-rendered pages
   - CSS selector configuration for targeting content
   - Examples: Meta AI, DeepMind Blog

3. **GitHub**:
   - Fetches releases via GitHub API
   - Can track commits and PRs (future)
   - Examples: OpenAI SDK, Anthropic SDK

4. **APIs** (future):
   - arXiv for research papers
   - News APIs for aggregated content

---

## Celery Tasks

### Scheduled Tasks (via Celery Beat)

```python
# High priority sources - every 2 hours
"scrape-high-priority-sources": crontab(minute=0, hour="*/2")

# Medium priority sources - every 6 hours
"scrape-medium-priority-sources": crontab(minute=0, hour="*/6")

# Low priority sources - daily at 2 AM
"scrape-low-priority-sources": crontab(minute=0, hour=2)
```

### Manual Tasks

- `scrape_source(source_id)` - Scrape a single source
- `scrape_all_sources()` - Scrape all active sources
- `scrape_priority_sources(priority)` - Scrape by priority level
- `sync_sources_to_db()` - Sync YAML config to database

---

## API Endpoints

### Source Management

```
GET    /api/v1/scraping/sources              # List all sources
GET    /api/v1/scraping/sources/{id}         # Get source details
POST   /api/v1/scraping/sources/sync         # Sync YAML to database
```

### Scraping Control

```
POST   /api/v1/scraping/scrape/{source_id}   # Trigger single source scrape
POST   /api/v1/scraping/scrape/all           # Trigger scrape for all sources
POST   /api/v1/scraping/scrape/priority/{p}  # Trigger scrape by priority
```

### Articles

```
GET    /api/v1/scraping/articles              # List scraped articles
GET    /api/v1/scraping/articles/stats        # Get statistics
```

### Task Monitoring

```
GET    /api/v1/scraping/tasks/{task_id}       # Get Celery task status
GET    /api/v1/scraping/health                # System health check
```

---

## Usage Examples

### 1. Initial Setup: Sync Sources to Database

```bash
curl -X POST http://localhost:8000/api/v1/scraping/sources/sync \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

Response:
```json
{
  "task_id": "abc123",
  "message": "Source sync task queued",
  "status_url": "/api/v1/scraping/tasks/abc123"
}
```

### 2. Manual Scrape: Single Source

```bash
curl -X POST http://localhost:8000/api/v1/scraping/scrape/openai_blog \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

Response:
```json
{
  "task_id": "def456",
  "source_id": "openai_blog",
  "message": "Scraping task queued for OpenAI Blog"
}
```

### 3. Manual Scrape: All High Priority Sources

```bash
curl -X POST http://localhost:8000/api/v1/scraping/scrape/priority/high \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 4. List Sources

```bash
curl http://localhost:8000/api/v1/scraping/sources?priority=high \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

Response:
```json
[
  {
    "id": "openai_blog",
    "name": "OpenAI Blog",
    "type": "rss",
    "url": "https://openai.com/blog/rss/",
    "check_interval_hours": 2,
    "priority": "high",
    "authority_score": 95,
    "active": true,
    "success_count": 45,
    "failure_count": 0,
    "last_checked_at": "2025-10-24T12:00:00Z",
    "next_check_at": "2025-10-24T14:00:00Z"
  }
]
```

### 5. List Recent Articles

```bash
curl "http://localhost:8000/api/v1/scraping/articles?limit=10" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 6. Get Article Statistics

```bash
curl http://localhost:8000/api/v1/scraping/articles/stats \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

Response:
```json
{
  "total_articles": 150,
  "by_status": {
    "pending": 20,
    "processing": 5,
    "completed": 120,
    "failed": 5
  },
  "top_sources": [
    {"source": "OpenAI Blog", "count": 35},
    {"source": "Anthropic News", "count": 28},
    {"source": "Google AI Blog", "count": 22}
  ]
}
```

### 7. Check Task Status

```bash
curl http://localhost:8000/api/v1/scraping/tasks/abc123 \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

Response:
```json
{
  "task_id": "abc123",
  "status": "SUCCESS",
  "result": {
    "success": true,
    "source_id": "openai_blog",
    "articles_scraped": 5,
    "articles_stored": 4,
    "duplicates_found": 1
  }
}
```

---

## Deduplication Strategy

The system handles duplicates in two ways:

### 1. URL-based Deduplication

- Check if `Article.source_url` already exists
- Skip if duplicate found (most common case)
- Prevents re-fetching the same article

### 2. Content Hash Deduplication

- Generate SHA-256 hash of title + content
- Check if `Article.content_hash` already exists
- If found: mark as duplicate, store reference to canonical article
- Useful for:
  - Same article from different sources
  - Republished content
  - Minor URL variations

Example:
```python
class Article:
    content_hash: str          # SHA-256 hash
    duplicate_of: UUID         # Reference to canonical article
    canonical: bool            # Is this the canonical version?
```

---

## Error Handling

### Source-Level Errors

Sources track their own health:
```python
class Source:
    success_count: int         # Number of successful scrapes
    failure_count: int         # Number of failed scrapes
    last_error: str            # Most recent error message
```

### Retry Logic

- Scraper tasks retry 3 times on failure
- Exponential backoff: 60s, 120s, 240s
- HTTP requests retry with exponential backoff: 1s, 2s, 4s

### Monitoring

- Celery task states: PENDING, STARTED, SUCCESS, FAILURE, RETRY
- Source health tracked in database
- Health check endpoint: `/api/v1/scraping/health`

---

## Docker Services

### Service Configuration

```yaml
# Celery Worker (4 concurrent workers)
worker:
  command: celery -A workers.celery_app worker --loglevel=info --concurrency=4
  depends_on: [postgres, redis]

# Celery Beat (scheduler)
beat:
  command: celery -A workers.celery_app beat --loglevel=info
  depends_on: [postgres, redis]
```

### Starting Services

```bash
# Start all services (API, worker, beat, postgres, redis)
docker-compose up -d

# View logs
docker-compose logs -f worker
docker-compose logs -f beat

# Monitor tasks
docker-compose exec worker celery -A workers.celery_app inspect active
```

---

## Testing

### Unit Tests

```bash
# Test scraper classes
pytest backend/tests/unit/test_scraper.py

# Test specific scraper
pytest backend/tests/unit/test_scraper.py::test_rss_scraper
```

### Integration Tests

```bash
# Test scraping tasks
pytest backend/tests/integration/test_scraping_tasks.py

# Test API endpoints
pytest backend/tests/integration/test_scraping_api.py
```

### Manual Testing

```bash
# 1. Sync sources to database
curl -X POST http://localhost:8000/api/v1/scraping/sources/sync \
  -H "Authorization: Bearer $TOKEN"

# 2. Trigger scrape
curl -X POST http://localhost:8000/api/v1/scraping/scrape/openai_blog \
  -H "Authorization: Bearer $TOKEN"

# 3. Check results
curl http://localhost:8000/api/v1/scraping/articles?source_id=openai_blog \
  -H "Authorization: Bearer $TOKEN"
```

---

## Performance Considerations

### Rate Limiting

- Task rate limit: 100 tasks/minute (configurable)
- HTTP timeout: 30 seconds
- Concurrent workers: 4 (configurable)

### Queue Prioritization

Tasks are routed to specific queues:
- `scraping`: Scraping tasks
- `processing`: Article processing (future)
- `digests`: Digest generation (future)
- `maintenance`: Cleanup tasks

### Caching

- Redis used as Celery broker and result backend
- Task results expire after 1 hour
- Consider caching:
  - Source configurations (reload on change)
  - Recent scraping results

---

## Future Enhancements

### Week 4 Improvements

- Implement article processing tasks (summarization)
- Add impact scoring
- Classification by companies/industries
- Sentiment analysis

### Future Features

- Social media integration (Twitter/X, Reddit)
- Custom user sources
- Webhook support for real-time updates
- Advanced deduplication (semantic similarity)
- Source health dashboard
- Auto-disable failing sources
- Custom scraping intervals per source

---

## Troubleshooting

### Issue: Tasks not executing

**Symptoms**: Scraping tasks queued but not running

**Solutions**:
```bash
# Check worker is running
docker-compose ps worker

# View worker logs
docker-compose logs -f worker

# Restart worker
docker-compose restart worker
```

### Issue: Beat schedule not triggering

**Symptoms**: No automatic scraping

**Solutions**:
```bash
# Check beat is running
docker-compose ps beat

# View beat logs
docker-compose logs -f beat

# Verify schedule
docker-compose exec beat celery -A workers.celery_app inspect scheduled
```

### Issue: Source scraping failing

**Symptoms**: High failure_count on source

**Solutions**:
1. Check `Source.last_error` in database
2. Test URL manually
3. Verify selectors for web scraping
4. Check rate limiting from source
5. Update User-Agent if blocked

### Issue: Duplicate articles

**Symptoms**: Same article stored multiple times

**Solutions**:
1. Check content hash generation
2. Verify URL normalization
3. Review deduplication logic
4. Consider semantic deduplication (future)

---

## Monitoring Checklist

Daily monitoring:
- [ ] Check `/api/v1/scraping/health` endpoint
- [ ] Review failing sources (failure_count > 3)
- [ ] Check articles scraped in last 24h
- [ ] Monitor Celery worker/beat status
- [ ] Review error logs

Weekly monitoring:
- [ ] Review source performance (success rate)
- [ ] Check for new duplicate patterns
- [ ] Analyze scraping costs (API usage)
- [ ] Update source configurations if needed

---

## Related Documentation

- MVP Roadmap: `docs/planning/mvp-roadmap.md` (Week 3)
- Database Schema: `docs/planning/database-api-spec.md`
- Technical Architecture: `docs/planning/technical-architecture.md`
- Article Processing (Week 4): `docs/features/summarization.md` (future)

---

**Status**: Production Ready ✅
**Next Phase**: Week 4 - AI Summarization & Classification
