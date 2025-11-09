---
type: pattern
name: API Data Transformation Layer
status: implemented
created: 2025-11-08
updated: 2025-11-08
files:
  - packages/backend-api/api/articles.py
  - packages/backend-api/api/rss_feeds.py
related:
  - .ai/knowledge/features/dashboard-overview.md
tags: [api, backend, data-transformation, schema-mapping, pattern]
---

# API Data Transformation Layer

## Pattern Overview

**Problem:** Frontend expects a specific data schema that differs from the database schema. Changing the database schema is risky (data migration) and tightly couples frontend to backend.

**Solution:** Transform data in the API layer during read operations, mapping database fields to frontend expectations.

**Use this pattern when:**
- Database schema differs from API contract
- Migrating old data to new schema is impractical
- Frontend and backend schemas need to evolve independently
- You need to handle missing/null fields gracefully
- Derived fields need calculation (e.g., extracting domain from URL)

## How It Works

### Architecture

```
┌──────────────┐
│   Frontend   │
│ expects:     │
│ - url        │
│ - description│
│ - published_at
└──────┬───────┘
       │ GET /api/articles
       ↓
┌──────────────────────┐
│  API Transform Layer │  ← This pattern
│  Maps:               │
│  • link → url        │
│  • summary → desc    │
│  • published → pub_at│
│  • Extract source    │
│  • Generate IDs      │
└──────┬───────────────┘
       │ MongoDB query
       ↓
┌──────────────┐
│   Database   │
│ stores:      │
│ - link       │
│ - summary    │
│ - published  │
└──────────────┘
```

### Implementation

**Step 1: Define API contract (frontend schema)**

```typescript
// Frontend expects this schema
interface Article {
  id: string;
  title: string;
  description?: string;
  url: string;
  published_at: string;
  source?: string;
}
```

**Step 2: Query database (backend schema)**

```python
# Database stores articles with different fields
articles = db.articles.find({}, {"_id": 0})
# Returns: {link, summary, published, ...}
```

**Step 3: Transform in API layer**

```python
# API endpoint (articles.py:62-92)
@router.get("/api/articles")
async def get_articles(db=Depends(get_db_client)):
    # 1. Fetch from database
    articles = list(db.articles.find({}, {"_id": 0}))

    # 2. Transform each record
    transformed = []
    for article in articles:
        # Handle missing/derived fields
        source = extract_source_from_url(article.get("link"))
        article_id = article.get("id") or str(uuid.uuid4())

        # Map to frontend schema
        transformed.append({
            "id": article_id,
            "title": article.get("title"),
            "description": article.get("summary"),      # summary → description
            "url": article.get("link"),                 # link → url
            "published_at": article.get("published"),   # published → published_at
            "source": source,                           # Derived field
        })

    # 3. Return standardized response
    return {"data": transformed}
```

**Step 4: Extract derived fields**

```python
def extract_source_from_url(link: str) -> str:
    """Extract source name from article URL."""
    if not link:
        return "RSS"

    from urllib.parse import urlparse
    domain = urlparse(link).netloc  # "www.techcrunch.com"
    source = domain.replace("www.", "").split(".")[0].title()  # "Techcrunch"
    return source or "RSS"
```

## Key Principles

### 1. Non-Destructive

**Don't:** Run database migrations to change existing records

**Do:** Transform on read, leave database unchanged

**Benefits:**
- No risk of data corruption
- Works with old and new records
- Easy to rollback (just change transformation logic)

### 2. Single Source of Truth

**Location:** API endpoint is the ONLY place where transformation happens

**Don't:** Transform in multiple places (service layer, frontend, etc.)

**Benefits:**
- Centralized logic for field mapping
- Easy to update when schema changes
- Consistent transformations across all clients

### 3. Graceful Degradation

**Handle missing fields:**
```python
article.get("id") or str(uuid.uuid4())  # Generate if missing
article.get("source") or "RSS"           # Default if missing
article.get("summary", "")               # Empty string fallback
```

**Handle null values:**
```python
link = article.get("link", "")
if link:
    # Extract domain
else:
    # Use default
```

### 4. Standardized Response Format

**Always wrap arrays in a `data` key:**
```python
return {"data": transformed}  # Not just: return transformed
```

**Benefits:**
- Consistent response shape across all endpoints
- Room for metadata (pagination, counts, etc.)
- Frontend can always expect `response.data.data`

## Code Examples

### Example 1: Field Renaming

**Database field:** `link`
**Frontend field:** `url`

```python
transformed.append({
    "url": article.get("link"),  # Rename
})
```

### Example 2: Generating Missing Fields

**Problem:** Old articles lack `id` field

```python
article_id = article.get("id") or str(uuid.uuid4())
transformed.append({
    "id": article_id,
})
```

### Example 3: Extracting Derived Fields

**Problem:** `source` not stored in database

```python
# Extract from URL
link = article.get("link", "")
if link:
    domain = urlparse(link).netloc
    source = domain.replace("www.", "").split(".")[0].title()
else:
    source = "RSS"

transformed.append({
    "source": source,
})
```

### Example 4: Type Conversions

**Problem:** Database stores datetime as string, frontend needs ISO format

```python
from datetime import datetime

published = article.get("published")
if isinstance(published, datetime):
    published_at = published.isoformat()
else:
    published_at = published  # Already string

transformed.append({
    "published_at": published_at,
})
```

## When to Use This Pattern

### ✅ Use when:
- Database schema differs from API contract
- Frontend and backend teams evolve independently
- Migrating data is risky or impractical
- Handling legacy data with missing fields
- Computing derived/calculated fields
- Supporting multiple API versions

### ❌ Don't use when:
- Database schema perfectly matches frontend needs
- Performance is critical (transformation adds overhead)
- Data is write-heavy (transformation on every write is expensive)
- Simple CRUD with no schema mismatch

## Performance Considerations

**Cost:** Transformation adds CPU overhead on each read

**Optimizations:**
1. **Limit fields fetched:** `db.find({}, {"_id": 0, "link": 1, "title": 1})`
2. **Pagination:** Transform only the requested page
3. **Caching:** Cache transformed results (Redis)
4. **Batch processing:** Transform in bulk for large datasets

**Benchmarks** (approximate):
- Transforming 100 articles: ~50ms
- Transforming 1000 articles: ~500ms
- Acceptable for < 10,000 records without pagination

## Related Patterns

### GraphQL Resolvers

Similar concept - resolvers transform database entities to GraphQL schema:

```typescript
// GraphQL resolver
const Article = {
  url: (parent) => parent.link,  // Field mapping
  description: (parent) => parent.summary,
};
```

### Data Transfer Objects (DTOs)

OOP pattern for transforming domain models to API responses:

```python
class ArticleDTO:
    def __init__(self, article: Article):
        self.id = article.id or str(uuid.uuid4())
        self.url = article.link
        self.description = article.summary
```

### Adapter Pattern

Wrap database results in an adapter that provides the expected interface:

```python
class ArticleAdapter:
    def __init__(self, db_article):
        self._article = db_article

    @property
    def url(self):
        return self._article.get("link")

    @property
    def description(self):
        return self._article.get("summary")
```

## Migration Path

**Phase 1:** Transform in API (current approach)

**Phase 2:** Migrate database schema when safe
- Write new records with correct schema
- Transform layer handles old records
- Eventually all records are new schema

**Phase 3:** Remove transformation layer
- Once all records migrated
- API reads directly from database
- No transformation overhead

## Testing Strategy

**Unit tests:**
```python
def test_transform_article():
    db_article = {
        "link": "https://example.com/article",
        "summary": "Test summary",
        "published": "2025-11-08T10:00:00"
    }

    result = transform_article(db_article)

    assert result["url"] == "https://example.com/article"
    assert result["description"] == "Test summary"
    assert result["published_at"] == "2025-11-08T10:00:00"
    assert result["id"] is not None
```

**Integration tests:**
```python
def test_get_articles_endpoint():
    response = client.get("/api/articles")

    assert response.status_code == 200
    assert "data" in response.json()

    articles = response.json()["data"]
    assert all("url" in a for a in articles)
    assert all("description" in a for a in articles)
```

## Common Pitfalls

### Pitfall 1: Forgetting to Handle Nulls

**Bad:**
```python
source = article["source"].upper()  # KeyError if missing!
```

**Good:**
```python
source = article.get("source", "RSS").upper()
```

### Pitfall 2: Transforming in Multiple Places

**Bad:**
```python
# Transform in API
articles = transform_articles(db_articles)

# ALSO transform in frontend
const mappedArticles = articles.map(a => ({ ...a, url: a.link }))
```

**Good:** Transform ONLY in API layer

### Pitfall 3: Not Standardizing Response Format

**Bad:**
```python
# Inconsistent response formats
return articles  # Sometimes array
return {"data": articles}  # Sometimes object
```

**Good:**
```python
# Always return {"data": ...}
return {"data": articles}
```

## Real-World Examples

**Example from this codebase:**

```python
# packages/backend-api/api/articles.py:62-92
@router.get("/api/articles")
async def get_articles(db=Depends(get_db_client)):
    articles = list(db.articles.find({}, {"_id": 0}))

    transformed = []
    for article in articles:
        # Extract source from URL domain
        source = article.get("source")
        if not source or source == "rss":
            link = article.get("link", "")
            if link:
                from urllib.parse import urlparse
                domain = urlparse(link).netloc
                source = domain.replace("www.", "").split(".")[0].title()
            else:
                source = "RSS"

        transformed.append({
            "id": article.get("id") or str(uuid.uuid4()),
            "title": article.get("title"),
            "description": article.get("summary"),
            "url": article.get("link"),
            "published_at": article.get("published"),
            "source": source,
        })

    return {"data": transformed}
```

**RSS Feeds endpoint:**

```python
# packages/backend-api/api/rss_feeds.py:44-48
@router.get("/api/rss_feeds")
async def get_rss_feeds(db=Depends(get_db_client)):
    feeds = list(db.rss_feeds.find({}, {"_id": 0}))
    return {"data": feeds}  # Standardized response
```

---

**Summary:** The API Data Transformation Layer pattern decouples frontend from database schema by transforming data during read operations. This enables independent evolution of frontend/backend, graceful handling of legacy data, and centralized field mapping logic.
