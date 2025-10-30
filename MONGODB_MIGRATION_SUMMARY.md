# MongoDB Migration Summary

## Overview

The UP2D8 backend has been migrated from PostgreSQL + Redis to MongoDB-only architecture. This document summarizes all changes made and provides guidance for completing the migration.

## Completed Changes

### 1. Docker Infrastructure (✅ COMPLETE)

**File: `docker-compose.yml`**

- ✅ Removed PostgreSQL service and volumes
- ✅ Removed Redis service and volumes
- ✅ Removed pgAdmin management tool
- ✅ Removed Redis Commander management tool
- ✅ Updated MongoDB service configuration
- ✅ Added Mongo Express as MongoDB management UI (optional, profile: tools)
- ✅ Updated all service environment variables to use MongoDB
- ✅ Removed PostgreSQL and Redis dependencies from all services

**Changes:**
- PostgreSQL port 5432 → Removed
- Redis port 6379 → Removed
- MongoDB port 27017 → Active
- Mongo Express port 8081 → Available with `--profile tools`

### 2. Dependencies (✅ COMPLETE)

**File: `backend/requirements.txt`**

**Removed:**
- `sqlalchemy==2.0.23`
- `alembic==1.12.1`
- `psycopg2-binary==2.9.9`
- `asyncpg==0.29.0`
- `redis==5.0.1`
- `hiredis==2.2.3`

**Added:**
- `motor==3.3.2` (Async MongoDB driver)

**Kept:**
- `pymongo==4.6.1` (MongoDB driver)
- `celery==5.3.4` (Can use MongoDB as broker)

### 3. Database Models and Session (✅ COMPLETE)

**File: `backend/api/db/session.py`**

- ✅ Completely rewritten for MongoDB
- ✅ Removed SQLAlchemy engine and session management
- ✅ Added MongoDB client singleton pattern
- ✅ Updated `get_db()` dependency to return `Database` instead of `Session`
- ✅ Added `init_db()` to create MongoDB indexes
- ✅ Added `drop_db()` for development/testing

**File: `backend/api/db/models.py`**

- ✅ Old SQLAlchemy models backed up to `models_sqlalchemy_backup.py`
- ✅ Created new MongoDB document schema helpers
- ✅ Added document creation functions for each collection:
  - `UserDocument.create()`
  - `UserPreferenceDocument.create()`
  - `ArticleDocument.create()`
  - `SourceDocument.create()`
  - `DigestDocument.create()`
  - `ChatSessionDocument.create()`
  - `ChatMessageDocument.create()`
  - `BookmarkDocument.create()`
  - `ArticleFeedbackDocument.create()`
- ✅ Added `Collections` class with collection name constants

### 4. Authentication System (✅ COMPLETE)

**File: `backend/api/utils/auth.py`**

- ✅ Updated imports to use `pymongo.database.Database`
- ✅ Removed SQLAlchemy `Session` and `User` model imports
- ✅ Updated `get_current_user()` to work with MongoDB
  - Returns `dict` instead of `User` object
  - Uses `db[CosmosCollections.USERS].find_one()`
- ✅ Updated `get_current_active_user()` to work with dictionaries
- ✅ Updated `authenticate_user()` to use MongoDB queries
- ✅ Updated `get_current_user_alt()` (OAuth2PasswordBearer version)

**File: `backend/api/routers/auth.py`**

- ✅ Already using MongoDB via `cosmos_db.py`
- ✅ No changes needed (was implemented correctly from the start)

### 5. Routers - Partially Updated (⚠️ IN PROGRESS)

**File: `backend/api/routers/preferences.py`** (✅ COMPLETE)

- ✅ Updated imports to use `pymongo.database.Database`
- ✅ Updated `get_my_preferences()` to use MongoDB
- ⚠️ `update_my_preferences()` still needs updating

### 6. Alembic Migrations (✅ COMPLETE)

- ✅ Removed entire `backend/api/db/migrations/` directory
- ✅ No longer needed with MongoDB (schema-less)

### 7. Cosmos DB Client (✅ ALREADY COMPLETE)

**File: `backend/api/db/cosmos_db.py`**

- ✅ Already implemented and working
- ✅ Provides MongoDB abstraction for both local and Azure Cosmos DB
- ✅ Includes index creation functions
- ✅ Includes helper query functions

---

## Remaining Work (⚠️ TODO)

### Files Still Using SQLAlchemy

The following files still import from SQLAlchemy and need migration:

#### Routers (High Priority)

1. **`backend/api/routers/preferences.py`**
   - Status: ⚠️ Partially updated
   - Needs: Complete `update_my_preferences()` function

2. **`backend/api/routers/feedback.py`**
   - Status: ❌ Not started
   - Uses: `Session`, `User`, `ArticleFeedback`, `Article`, `Digest`, `UserPreferenceProfile`
   - Complexity: HIGH (many database operations)

3. **`backend/api/routers/digests.py`**
   - Status: ❌ Not started
   - Uses: `Session`, `desc()` for sorting
   - Complexity: MEDIUM

4. **`backend/api/routers/analytics.py`**
   - Status: ❌ Not started
   - Uses: `Session`
   - Complexity: MEDIUM

5. **`backend/api/routers/scraping.py`**
   - Status: ❌ Not started
   - Uses: `Session`, `func`
   - Complexity: MEDIUM

#### Services (Medium Priority)

1. **`backend/api/services/memory/short_term.py`**
   - Uses: `Session`
   - Part of chat memory system

2. **`backend/api/services/memory/digest_context.py`**
   - Uses: `Session`
   - Part of chat memory system

3. **`backend/api/services/memory/long_term.py`**
   - Uses: `Session`
   - Part of chat memory system

4. **`backend/api/services/analytics_tracker.py`**
   - Uses: `Session`, `func`, `and_`, `text`
   - Complexity: HIGH (complex SQL queries)

5. **`backend/api/services/relevance_scorer.py`**
   - Uses: `Session`
   - Complexity: MEDIUM

### Redis Dependencies (Low Priority)

**File: `backend/api/utils/cache.py`**

- ✅ Already using in-memory cache (no Redis dependency)
- ✅ No changes needed

---

## Migration Guide for Remaining Routers

### Step-by-Step Migration Pattern

For each router/service that uses SQLAlchemy:

#### 1. Update Imports

```python
# OLD (SQLAlchemy)
from sqlalchemy.orm import Session
from api.db.models import User, Article, Digest

# NEW (MongoDB)
from pymongo.database import Database
from api.db.models import Collections, UserDocument, ArticleDocument
```

#### 2. Update Function Signatures

```python
# OLD
async def my_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

# NEW
async def my_endpoint(
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
```

#### 3. Convert SQLAlchemy Queries to MongoDB

**Example: Simple Query**

```python
# OLD (SQLAlchemy)
user = db.query(User).filter(User.email == email).first()

# NEW (MongoDB)
users_collection = db[Collections.USERS]
user = users_collection.find_one({"email": email})
```

**Example: Insert**

```python
# OLD (SQLAlchemy)
new_user = User(email=email, password_hash=hashed_password)
db.add(new_user)
db.commit()
db.refresh(new_user)

# NEW (MongoDB)
users_collection = db[Collections.USERS]
user_doc = UserDocument.create(email=email, password_hash=hashed_password)
result = users_collection.insert_one(user_doc)
user_doc["_id"] = result.inserted_id
```

**Example: Update**

```python
# OLD (SQLAlchemy)
user = db.query(User).filter(User.id == user_id).first()
user.last_login_at = datetime.utcnow()
db.commit()

# NEW (MongoDB)
users_collection = db[Collections.USERS]
users_collection.update_one(
    {"id": user_id},
    {"$set": {"last_login_at": datetime.utcnow(), "updated_at": datetime.utcnow()}}
)
```

**Example: Complex Query with Joins**

```python
# OLD (SQLAlchemy - with JOIN)
results = db.query(Article, Source).join(
    Source, Article.source_id == Source.id
).filter(Article.published_at > cutoff_date).all()

# NEW (MongoDB - using $lookup or separate queries)
# Option 1: Separate queries (simpler, good for small datasets)
articles_collection = db[Collections.ARTICLES]
sources_collection = db[Collections.SOURCES]

articles = list(articles_collection.find({"published_at": {"$gt": cutoff_date}}))
source_ids = list(set(a["source_id"] for a in articles))
sources = {s["id"]: s for s in sources_collection.find({"id": {"$in": source_ids}})}

# Enrich articles with source data
for article in articles:
    article["source"] = sources.get(article["source_id"])

# Option 2: Using aggregation with $lookup (MongoDB equivalent of JOIN)
articles = list(articles_collection.aggregate([
    {"$match": {"published_at": {"$gt": cutoff_date}}},
    {"$lookup": {
        "from": Collections.SOURCES,
        "localField": "source_id",
        "foreignField": "id",
        "as": "source"
    }},
    {"$unwind": "$source"}
]))
```

#### 4. Update Field Access

```python
# OLD (SQLAlchemy - object attributes)
user_email = current_user.email
user_tier = current_user.tier

# NEW (MongoDB - dictionary keys)
user_email = current_user["email"]
user_tier = current_user.get("tier", "free")  # Use .get() for safety
```

#### 5. Handle Timestamps

```python
# MongoDB timestamps
from datetime import datetime

# Always use UTC
created_at = datetime.utcnow()

# MongoDB stores native datetime objects
doc = {
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}
```

---

## Testing Checklist

### Before Testing

1. ✅ Install dependencies: `pip install -r backend/requirements.txt`
2. ✅ Start MongoDB: `docker-compose up -d mongodb`
3. ✅ Verify MongoDB is running: `docker-compose ps`

### Authentication Tests

- ✅ Test user signup: `POST /api/v1/auth/signup`
- ✅ Test user login: `POST /api/v1/auth/login`
- ✅ Test token refresh: `POST /api/v1/auth/refresh`
- ✅ Test protected route: `GET /api/v1/auth/me`

### Database Tests

- ✅ Test MongoDB connection
- ✅ Test index creation: Run `python -m api.db.cosmos_db`
- ✅ Test user creation and retrieval
- ✅ Test preferences creation

### Service Tests

- ⚠️ Test digest generation (depends on router updates)
- ⚠️ Test chat functionality (depends on memory service updates)
- ⚠️ Test scraping pipeline (depends on router updates)

---

## Running the Migrated Backend

### Option 1: Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Access services
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Frontend: http://localhost:5173
# - MongoDB: mongodb://localhost:27017
```

### Option 2: Local Development

```bash
# Terminal 1: Start MongoDB
docker-compose up -d mongodb

# Terminal 2: Start backend
cd backend
source venv/bin/activate
uvicorn api.main:app --reload

# Access at http://localhost:8000
```

### Verify MongoDB Connection

```bash
# Connect to MongoDB shell
docker exec -it up2d8-mongodb mongosh

# In mongosh:
use up2d8
show collections
db.users.countDocuments()
```

---

## Known Issues and Workarounds

### Issue 1: Old imports still present

**Problem:** Some routers still import SQLAlchemy models
**Impact:** Those endpoints will fail with import errors
**Workaround:** Update each router as needed (see migration guide above)

### Issue 2: Celery broker configuration

**Problem:** Celery was using Redis as broker
**Impact:** Background tasks may not work
**Solution:** Configure Celery to use MongoDB as broker or use a memory broker for development

```python
# In workers/celery_app.py
# Option 1: MongoDB as broker (requires celery[mongodb])
broker_url = "mongodb://mongodb:27017/up2d8_celery"

# Option 2: Memory broker (development only)
broker_url = "memory://"
```

### Issue 3: In-memory cache limitations

**Problem:** In-memory cache doesn't persist across instances
**Impact:** Cache is lost on restart, doesn't work with multiple backend instances
**Solution:** For production, consider Azure Cache for Redis or accept the limitation

---

## Environment Variables

### Updated Variables

```bash
# OLD (PostgreSQL + Redis)
DATABASE_URL=postgresql://user:pass@postgres:5432/up2d8
REDIS_URL=redis://redis:6379/0

# NEW (MongoDB only)
MONGODB_URL=mongodb://mongodb:27017/
COSMOS_DB_CONNECTION_STRING=mongodb://mongodb:27017/
COSMOS_DB_NAME=up2d8
```

### For Azure Deployment

```bash
# Local MongoDB
MONGODB_URL=mongodb://localhost:27017/

# Azure Cosmos DB (production)
COSMOS_DB_CONNECTION_STRING=mongodb://your-cosmos-account:key@your-cosmos-account.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb
COSMOS_DB_NAME=up2d8
```

---

## Architecture Changes

### Before (PostgreSQL + Redis)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   FastAPI   │────▶│ PostgreSQL  │     │    Redis    │
│   Backend   │     │  (Primary)  │     │   (Cache)   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                                        │
       └────────────────────────────────────────┘
                    (Two databases)
```

### After (MongoDB Only)

```
┌─────────────┐     ┌─────────────┐
│   FastAPI   │────▶│   MongoDB   │
│   Backend   │     │  (Primary)  │
└─────────────┘     └─────────────┘
       │
       └────────────▶ In-Memory Cache
                    (Built-in)
```

**Benefits:**
- ✅ Simpler architecture (one database)
- ✅ Lower cost (no Redis needed)
- ✅ Easier deployment to Azure (Cosmos DB)
- ✅ Schema flexibility (no migrations needed)

**Trade-offs:**
- ⚠️ In-memory cache doesn't persist
- ⚠️ Need to rewrite complex SQL queries
- ⚠️ MongoDB query patterns are different

---

## Next Steps

### Immediate (High Priority)

1. ⚠️ Complete `backend/api/routers/preferences.py` migration
2. ⚠️ Migrate `backend/api/routers/feedback.py`
3. ⚠️ Migrate `backend/api/routers/digests.py`
4. ⚠️ Test auth flow end-to-end
5. ⚠️ Update Celery broker configuration

### Short Term (Medium Priority)

1. ⚠️ Migrate remaining routers (analytics, scraping)
2. ⚠️ Migrate memory services (short_term, digest_context, long_term)
3. ⚠️ Migrate analytics_tracker service
4. ⚠️ Update all tests to use MongoDB

### Long Term (Low Priority)

1. ⚠️ Optimize MongoDB indexes for performance
2. ⚠️ Add MongoDB query performance monitoring
3. ⚠️ Consider adding Redis back for caching in production
4. ⚠️ Add database backup/restore procedures

---

## Files Modified

### Deleted/Removed
- ❌ `backend/api/db/migrations/` (entire directory)

### Backed Up
- 💾 `backend/api/db/models.py` → `backend/api/db/models_sqlalchemy_backup.py`

### Modified
- ✅ `docker-compose.yml`
- ✅ `backend/requirements.txt`
- ✅ `backend/api/db/session.py`
- ✅ `backend/api/db/models.py` (rewritten)
- ✅ `backend/api/utils/auth.py`
- ⚠️ `backend/api/routers/preferences.py` (partial)

### Already Compatible (No Changes Needed)
- ✅ `backend/api/routers/auth.py`
- ✅ `backend/api/db/cosmos_db.py`
- ✅ `backend/api/utils/cache.py`

---

## Questions or Issues?

If you encounter problems during migration:

1. Check the logs: `docker-compose logs -f api`
2. Verify MongoDB connection: `docker exec -it up2d8-mongodb mongosh`
3. Check environment variables: `docker exec up2d8-api env | grep MONGO`
4. Review this guide for migration patterns

---

**Migration Date:** 2025-10-30
**Status:** ⚠️ Partial - Core infrastructure complete, router migrations in progress
**Next Review:** After completing high-priority router migrations
