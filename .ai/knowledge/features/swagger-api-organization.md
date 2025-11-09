---
type: feature
name: Swagger API Organization
status: implemented
created: 2025-11-09
updated: 2025-11-09
files:
  - packages/backend-api/main.py:30-46
  - packages/backend-api/api/health.py:6
  - packages/backend-api/api/analytics.py:7
  - packages/backend-api/api/topics.py:8
  - packages/backend-api/api/rss_feeds.py:9
  - packages/backend-api/api/articles.py:8
  - packages/backend-api/api/feedback.py:7
  - packages/backend-api/api/users.py:8
  - packages/backend-api/api/chat.py:9
related:
  - ../components/backend-api-architecture.md
tags: [api, swagger, openapi, documentation, fastapi, tags]
---

# Swagger API Organization

## What It Does
Organizes the FastAPI Swagger documentation into logical, tagged groups with descriptions, making it easy for developers to explore and understand the 24 API endpoints. Transforms a flat, unorganized API list into a well-structured, categorized interface.

## Before and After

**Before (Unorganized):**
```
/api/health
/api/auth/me
/api/auth/protected
/api/analytics
/api/topics/suggest
/api/rss_feeds
/api/rss_feeds/{feed_id}
...all 24 endpoints in one flat list
```

**After (Organized by Tags):**
```
System (2 endpoints)
  ├─ GET /api/health
  └─ GET /

Authentication (2 endpoints)
  ├─ GET /api/auth/me
  └─ GET /api/auth/protected

Chat (5 endpoints)
  ├─ POST /api/chat
  ├─ POST /api/sessions
  └─ ...

[8 more categorized groups]
```

## How It Works
Uses FastAPI's `openapi_tags` metadata and router-level `tags` parameter to organize endpoints:

**Key files:**
- `packages/backend-api/main.py:30-46` - OpenAPI tags configuration with descriptions
- `packages/backend-api/api/*.py` - Router tag assignments

### Tag Structure

| Tag | Endpoints | Purpose |
|-----|-----------|---------|
| **System** | 2 | Health checks, root endpoint |
| **Authentication** | 2 | Login, user profile |
| **Users** | 4 | User CRUD, preferences |
| **Articles** | 3 | Article management |
| **RSS Feeds** | 5 | Feed CRUD operations |
| **Topics** | 1 | AI topic suggestions |
| **Chat** | 5 | AI chat sessions and messages |
| **Analytics** | 1 | Event tracking |
| **Feedback** | 1 | User feedback |
| **Total** | 24 | All API endpoints |

### Implementation Details

**main.py - OpenAPI Configuration:**
```python
app = FastAPI(
    title="UP2D8 Backend API",
    version="1.0.0",
    description="Personal news digest and information management platform API",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "System", "description": "System health and monitoring endpoints"},
        {"name": "Authentication", "description": "User authentication and authorization"},
        {"name": "Users", "description": "User management and preferences"},
        {"name": "Articles", "description": "Article content management"},
        {"name": "RSS Feeds", "description": "RSS feed subscriptions and management"},
        {"name": "Topics", "description": "AI-powered topic discovery and suggestions"},
        {"name": "Chat", "description": "AI chat sessions and message history"},
        {"name": "Analytics", "description": "Event tracking and analytics"},
        {"name": "Feedback", "description": "User feedback collection"},
    ],
)
```

**Router File Pattern:**
```python
# Before
router = APIRouter()

# After
router = APIRouter(tags=["Chat"])
```

## Important Decisions

- **9 Tag Categories**: Balanced granularity
  - Not too few (everything in "API")
  - Not too many (one tag per endpoint)
  - Logical groupings by domain

- **Tag Naming Convention**: Use nouns, not verbs
  - ✅ "Chat" (noun) not "Chatting" (verb)
  - ✅ "Users" (noun) not "User Management" (verbose)
  - Exception: "Authentication" (accepted standard)

- **Tag Descriptions**: Keep concise (one line)
  - Explain what the category is for
  - No implementation details
  - Focus on developer use cases

- **Alphabetical Ordering**: Tags appear in definition order
  - System first (most frequently checked)
  - Authentication second (common)
  - Alphabetical for the rest

## Usage Example

**Adding tags to a new router:**
```python
# api/new_feature.py
from fastapi import APIRouter

router = APIRouter(tags=["Feature Name"])

@router.get("/api/new_feature")
async def get_feature():
    return {"data": "..."}
```

**Updating tag descriptions:**
```python
# main.py
openapi_tags=[
    {"name": "New Tag", "description": "Brief description of what this tag covers"},
]
```

**Viewing Swagger UI:**
```bash
# Start the backend
uvicorn main:app --reload

# Visit in browser
http://localhost:8000/docs
```

## Testing

**Manual Testing:**
1. Start backend: `uvicorn main:app --reload`
2. Navigate to: `http://localhost:8000/docs`
3. Verify:
   - All 24 endpoints visible
   - Grouped by 9 tags
   - Each tag has a description
   - Tags are collapsible/expandable
   - Endpoints within tags are organized

**Automated OpenAPI Schema Validation:**
```bash
# Get OpenAPI schema
curl http://localhost:8000/openapi.json | python -m json.tool

# Check tags are present
curl http://localhost:8000/openapi.json | grep -o '"tags":\[.*?\]' | head -5
```

## Common Issues

### Issue: Endpoints not showing under tags
**Cause**: Router doesn't have `tags` parameter

**Solution**:
```python
router = APIRouter(tags=["Category Name"])
```

### Issue: Tag appears but no description
**Cause**: Tag not in `openapi_tags` array in main.py

**Solution**: Add to main.py:
```python
{"name": "YourTag", "description": "Your description"}
```

### Issue: Duplicate endpoints across tags
**Cause**: Router has multiple tags

**Solution**: Stick to one tag per router file:
```python
# Don't do this
router = APIRouter(tags=["Tag1", "Tag2"])  # ❌

# Do this
router = APIRouter(tags=["Tag1"])  # ✅
```

## Related Knowledge
- [Backend API Architecture](../components/backend-api-architecture.md) - Overall FastAPI structure

## Future Ideas
- [ ] Add response model examples to Swagger for each endpoint
- [ ] Include authentication requirements in OpenAPI schema
- [ ] Add request/response examples for complex endpoints
- [ ] Group tags into sections (Public API vs Internal API)
- [ ] Add API versioning to tags (v1, v2)
- [ ] Include rate limiting info in endpoint descriptions
- [ ] Add links to related documentation in descriptions
- [ ] Generate API client from OpenAPI schema
- [ ] Add deprecation warnings for old endpoints
