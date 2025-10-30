# Claude Code Configuration for UP2D8

## Project Context

UP2D8 is an AI-powered industry insight platform that delivers personalized daily digests via email with conversational AI chat for deeper exploration.

**Current Phase**: Backend Development (MVP Week 1-8)
**Focus**: Build backend API, scrapers, AI summarization, and digest generation before starting frontend
**Cost Strategy**: Use 100% free services during development (Ollama, ChromaDB, console email), migrate to paid services only when ready for production testing

---

## Documentation Guidelines

### Location & Organization

All documentation must be stored in the `docs/` directory with this structure:

```
docs/
├── planning/              # Original planning documents (READ-ONLY)
│   ├── README.md
│   ├── product-requirements.md
│   ├── technical-architecture.md
│   ├── mvp-roadmap.md
│   ├── database-api-spec.md
│   └── quick-start-guide.md
│
├── architecture/          # System design documentation
│   ├── overview.md       # High-level architecture
│   ├── conversational-ai-agent.md  # LangChain/LangGraph agent (Weeks 10-11)
│   ├── services/         # Service-specific docs
│   │   ├── llm-provider.md
│   │   ├── embeddings.md
│   │   ├── vector-db.md
│   │   └── email-provider.md
│   ├── data-models.md    # Database schemas, relationships
│   └── api-design.md     # API endpoints, contracts
│
├── development/          # Development guides
│   ├── setup.md         # Getting started
│   ├── testing.md       # Testing strategy
│   ├── workflows.md     # Git flow, PR process
│   └── troubleshooting.md
│
├── features/            # Feature documentation
│   ├── authentication.md
│   ├── content-aggregation.md
│   ├── summarization.md
│   ├── digest-generation.md
│   └── chat-rag.md
│
├── deployment/          # Production guides
│   ├── infrastructure.md
│   ├── monitoring.md
│   └── migration.md
│
└── decisions/           # Architecture Decision Records (ADRs)
    ├── 001-free-tier-abstraction.md
    ├── 002-provider-pattern.md
    └── template.md
```

### Documentation Rules

1. **When Adding New Features**:
   - Create or update `docs/features/{feature-name}.md`
   - Include: Purpose, Design, API endpoints, Examples, Testing
   - Reference related services in `docs/architecture/services/`

2. **When Making Architecture Decisions**:
   - Create new ADR in `docs/decisions/`
   - Use format: `NNN-decision-title.md`
   - Include: Context, Decision, Consequences, Alternatives

3. **When Modifying Services**:
   - Update corresponding doc in `docs/architecture/services/`
   - Document interface changes, new providers, configuration options

4. **When Adding Dependencies**:
   - Update `backend/requirements.txt`
   - Document WHY in commit message
   - Note if it's dev-only, free-tier, or paid-tier

---

## Testing Guidelines

### Test Organization

```
backend/tests/
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_llm_provider.py
│   ├── test_embeddings.py
│   ├── test_vector_db.py
│   ├── test_email_provider.py
│   ├── services/
│   │   ├── test_scraper.py
│   │   ├── test_summarizer.py
│   │   └── test_digest_generator.py
│   └── utils/
│       └── test_helpers.py
│
├── integration/             # Integration tests (with DB, Redis)
│   ├── test_api_auth.py
│   ├── test_api_articles.py
│   ├── test_api_digests.py
│   ├── test_api_chat.py
│   ├── test_scraping_pipeline.py
│   └── test_digest_pipeline.py
│
├── e2e/                    # End-to-end tests (full workflows)
│   ├── test_user_onboarding.py
│   ├── test_digest_delivery.py
│   └── test_chat_session.py
│
├── fixtures/               # Shared test data
│   ├── sample_articles.json
│   ├── sample_users.json
│   └── mock_responses.py
│
└── conftest.py            # Pytest configuration & fixtures
```

### Testing Standards

1. **Unit Tests** (`backend/tests/unit/`):
   - Test individual functions/classes in isolation
   - Mock external dependencies (DB, APIs, LLMs)
   - Fast execution (< 1 second per test)
   - Run on every commit

2. **Integration Tests** (`backend/tests/integration/`):
   - Test service interactions
   - Use test MongoDB database (Docker)
   - Mock external APIs only (Ollama, email)
   - Run before PR merge

3. **E2E Tests** (`backend/tests/e2e/`):
   - Test complete user workflows
   - Use test MongoDB database
   - Mock expensive operations (LLM calls)
   - Run before releases

### Test Commands

```bash
# Run all tests
pytest

# Run unit tests only (fast)
pytest backend/tests/unit/ -v

# Run integration tests
pytest backend/tests/integration/ -v

# Run specific test file
pytest backend/tests/unit/test_llm_provider.py -v

# Run with coverage
pytest --cov=api --cov-report=html

# Run tests matching pattern
pytest -k "test_ollama"
```

### Test Writing Guidelines

**Good Test Example**:
```python
# backend/tests/unit/test_llm_provider.py
import pytest
from api.services.llm_provider import OllamaClient

@pytest.mark.asyncio
async def test_ollama_generate_returns_text():
    """Test that OllamaClient.generate returns a string response."""
    client = OllamaClient(base_url="http://localhost:11434")

    result = await client.generate(
        prompt="Say hello",
        max_tokens=50
    )

    assert isinstance(result, str)
    assert len(result) > 0
```

---

## Development Workflow

### Backend-First Approach

**Current Phase: Backend Development (Weeks 1-8)**

**Order of Implementation**:
1. ✅ Infrastructure setup (Docker, env configs)
2. → Database models & migrations (Week 1)
3. → Authentication system (Week 1-2)
4. → Content scraping pipeline (Week 3)
5. → AI summarization (Week 4)
6. → Digest generation (Week 5-6)
7. → Email delivery (Week 6-7)
8. → RAG chat system (Week 7-8)

### Frontend Development**: Start in Week 9 after backend is solid

### Azure Deployment Architecture

UP2D8 uses Azure's free/low-cost services for deployment:

```
┌──────────────────────────────────────────────────────────┐
│                        AZURE CLOUD                        │
│                                                           │
│  ┌────────────────────┐         ┌──────────────────────┐ │
│  │  Azure Static Web  │         │   Azure Web App      │ │
│  │     App (F1)       │────────>│   (Free Tier)        │ │
│  │   (Frontend:       │  API    │   (Backend:          │ │
│  │   React + Vite)    │  Calls  │   FastAPI + Python)  │ │
│  └────────────────────┘         └──────────────────────┘ │
│                                           │               │
│                                           │               │
│                                           v               │
│                                  ┌────────────────────┐   │
│                                  │  Azure Cosmos DB   │   │
│                                  │  (MongoDB API)     │   │
│                                  │  Free Tier: 1000   │   │
│                                  │  RU/s, 25GB        │   │
│                                  └────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

#### Backend (Azure Web App - Free Tier)
1. Create Azure Web App resource (Free/F1 tier)
2. Configure Python runtime
3. Set up environment variables in App Settings:
   - MONGODB_URL (Cosmos DB connection string)
   - JWT_SECRET_KEY
   - LLM_PROVIDER=anthropic (or openai)
   - API keys for production services
4. Set up GitHub Actions deployment workflow
5. Configure startup command: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app`
6. Monitor logs and performance in Azure Portal

#### Frontend (Azure Static Web Apps)
1. Create Static Web App resource (Free tier)
2. Link to GitHub repository (auto-deploys on push)
3. Configure build settings:
   - App location: `/frontend`
   - Build command: `npm run build`
   - Output location: `dist`
4. Set up environment variables (.env for Vite):
   - VITE_API_URL=https://your-backend.azurewebsites.net
5. Configure API proxy rules if needed in `staticwebapp.config.json`

#### Database (Azure Cosmos DB with MongoDB API)
1. Create Cosmos DB account with MongoDB API
2. Choose **Free Tier** (1000 RU/s, 25GB storage)
3. Configure network access:
   - Add Azure Web App outbound IPs
   - Add developer IPs for local testing
4. Create database: `up2d8`
5. Create collections: `users`, `user_preferences`, `articles`, `digests`, `chat_messages`
6. Get connection string from Azure Portal
7. Add connection string to Azure Web App environment variables

#### Cost Optimization
- **Free Tier Components**:
  - Azure Static Web Apps: 100GB bandwidth/month (Free)
  - Azure Web App: F1 tier (60 CPU minutes/day, 1GB memory, 1GB storage)
  - Cosmos DB: Free tier (1000 RU/s, 25GB) - sufficient for MVP
- **Estimated Monthly Cost**: $0 during development, ~$0-5 for low traffic production

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/authentication-system

# Make changes with tests
# ... code ...

# Run tests before committing
pytest backend/tests/

# Commit with descriptive message
git commit -m "feat: implement JWT authentication

- Add user registration endpoint
- Add login with JWT token generation
- Add token refresh mechanism
- Add auth dependency for protected routes

Tests: backend/tests/integration/test_api_auth.py
Docs: docs/features/authentication.md"

# Push and create PR
git push origin feature/authentication-system
```

---

## Environment Configuration

### Development (.env.development)

**Priority**: Keep everything FREE
```bash
# Database
MONGODB_URL=mongodb://localhost:27017/up2d8

# AI Services
LLM_PROVIDER=ollama              # FREE - local
OLLAMA_MODEL=llama3.2:3b         # Fast, good quality
EMBEDDING_PROVIDER=sentence-transformers  # FREE - local
VECTOR_DB_PROVIDER=chroma        # FREE - local

# Email
EMAIL_PROVIDER=console           # FREE - logs only
```

**Never add these until explicitly discussed**:
- ANTHROPIC_API_KEY
- OPENAI_API_KEY
- PINECONE_API_KEY
- AWS credentials

### Production (.env.production)

**Only use when ready for production testing** (Week 12+)
```bash
# Database (Azure Cosmos DB with MongoDB API)
MONGODB_URL=mongodb://your-cosmos-account.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@your-cosmos-account@

# AI Services
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxx
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxx

# Azure Services
AZURE_WEBAPP_URL=https://your-webapp.azurewebsites.net
AZURE_STATIC_WEB_APP_URL=https://your-staticapp.azurestaticapps.net
AZURE_EMAIL_CONNECTION_STRING=...  # Azure Communication Services (optional)

# JWT Configuration (Production - use strong secrets!)
JWT_SECRET_KEY=generate_a_secure_random_key_here_min_64_chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### When to Upgrade

**Stay FREE if**:
- Building features (Weeks 1-10)
- Testing locally
- < 10 test users
- Learning/iterating

**Consider Groq (still FREE tier)** if:
- Need faster responses than Ollama
- Testing with 10-20 users
- Validating prompts

**Upgrade to PAID** only when:
- Week 11-12: Beta launch imminent
- 50+ real users
- Quality matters for UX
- Explicitly discussed and approved

---

## Code Standards

### Backend Structure

```
backend/
├── api/
│   ├── main.py              # FastAPI app
│   ├── routers/             # API endpoints
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── articles.py
│   │   ├── digests.py
│   │   └── chat.py
│   ├── models/              # Pydantic models (request/response schemas)
│   ├── services/            # Business logic
│   │   ├── llm_provider.py
│   │   ├── embeddings.py
│   │   ├── vector_db.py
│   │   ├── email_provider.py
│   │   ├── scraper.py
│   │   ├── summarizer.py
│   │   └── digest_generator.py
│   ├── db/                  # Database
│   │   ├── mongodb.py       # MongoDB connection & client
│   │   ├── models.py        # MongoDB document models (ODM)
│   │   └── repositories/    # Data access layer (optional pattern)
│   └── utils/
├── workers/                 # Background tasks (optional Celery/APScheduler)
│   ├── celery_app.py
│   └── tasks.py
├── tests/                   # All tests here
├── requirements.txt
└── Dockerfile.local         # Local Docker build
```

### Code Quality

**Before every commit**:
```bash
# Format code
black backend/

# Lint
ruff backend/

# Type check
mypy backend/

# Run tests
pytest
```

### Import Order

```python
# Standard library
import os
from typing import List, Optional
from datetime import datetime

# Third-party
from fastapi import FastAPI, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import httpx

# Local
from api.services.llm_provider import get_llm_client
from api.db.models import User
from api.utils.auth import verify_token
```

---

## AI Service Guidelines

### Provider Selection

**Development (Default)**:
- LLM: Ollama (llama3.2:3b)
- Embeddings: sentence-transformers (all-MiniLM-L6-v2)
- Vector DB: ChromaDB
- Email: Console

**Never hardcode providers**:
```python
# ❌ Bad - hardcoded
from anthropic import Anthropic
client = Anthropic(api_key="...")

# ✅ Good - abstracted
from api.services.llm_provider import get_llm_client
client = get_llm_client()
```

### Cost Consciousness

**Always**:
- Cache LLM responses aggressively
- Limit article count in dev: `MAX_ARTICLES_PER_SCRAPE=10`
- Use smaller models in dev: `llama3.2:3b` not `mistral:7b`
- Mock expensive calls in tests

**Monitor**:
- Log token usage for each LLM call
- Track embedding generation count
- Monitor vector DB storage size

---

## Common Tasks Reference

### Create New API Endpoint

1. Define route in `backend/api/routers/`
2. Add Pydantic models in `backend/api/models/`
3. Implement logic in `backend/api/services/`
4. Write tests in `backend/tests/integration/`
5. Document in `docs/architecture/api-design.md`

### Add New Service Provider

1. Create implementation in appropriate service file
2. Implement abstract base class interface
3. Add factory logic
4. Add env var configuration
5. Write unit tests
6. Update `docs/architecture/services/{service}.md`

### Database Changes (MongoDB)

**MongoDB is schemaless, but we maintain structure through:**

1. **Document Models** (`backend/api/db/models.py`):
   - Define Pydantic models for document structure
   - Use for validation and type hints
   - Example:
     ```python
     from pydantic import BaseModel, Field
     from datetime import datetime
     from typing import Optional

     class User(BaseModel):
         id: str = Field(alias="_id")
         email: str
         password_hash: str
         created_at: datetime

         class Config:
             populate_by_name = True
     ```

2. **Schema Validation** (optional, for production):
   - MongoDB supports JSON Schema validation
   - Add validators when creating collections:
     ```python
     db.create_collection("users", validator={
         "$jsonSchema": {
             "bsonType": "object",
             "required": ["email", "password_hash"],
             "properties": {
                 "email": {"bsonType": "string"},
                 "password_hash": {"bsonType": "string"}
             }
         }
     })
     ```

3. **Indexes**:
   - Create indexes for performance:
     ```python
     # In backend/api/db/mongodb.py or startup
     db.users.create_index("email", unique=True)
     db.users.create_index("created_at")
     db.articles.create_index([("user_id", 1), ("created_at", -1)])
     ```

4. **Migration Pattern** (no Alembic needed):
   - **For adding fields**: Just add to code, MongoDB auto-creates
   - **For renaming fields**: Use `$rename` update operation
   - **For removing fields**: Use `$unset` update operation
   - **For data transformations**: Write Python migration scripts
   - Keep migration scripts in `backend/scripts/migrations/`

   Example migration script:
   ```python
   # backend/scripts/migrations/001_add_tier_field.py
   from api.db.mongodb import get_database

   async def migrate():
       db = await get_database()
       result = await db.users.update_many(
           {"tier": {"$exists": False}},
           {"$set": {"tier": "free"}}
       )
       print(f"Updated {result.modified_count} users")
   ```

5. **Always**:
   - Test changes in local MongoDB first
   - Document schema changes in `docs/architecture/data-models.md`
   - Consider backward compatibility
   - Add validation in Pydantic models

### Add New Dependency

1. Add to `backend/requirements.txt`
2. Specify version: `package==1.2.3`
3. Note if free/paid in comments
4. Document why in commit message

---

## Key Principles

1. **Backend First**: Get API working before frontend
2. **Free First**: Use Ollama/ChromaDB until production
3. **Test Everything**: Unit + integration tests required
4. **Document Changes**: Update docs/ with every feature
5. **Provider Agnostic**: Never hardcode LLM/DB providers
6. **Environment Driven**: All config via .env files
7. **Cost Conscious**: Monitor usage, cache aggressively

---

## Quick Reference

### Start Development

#### Option 1: Docker Compose (Recommended)

```bash
# Start all services (MongoDB, backend, frontend)
docker-compose up

# Or run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop all services
docker-compose down

# Rebuild after changes
docker-compose up --build

# Services will be available at:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - MongoDB: mongodb://localhost:27017
```

**docker-compose.yml structure**:
```yaml
services:
  mongodb:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_DATABASE: up2d8

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.local
    ports:
      - "8000:8000"
    environment:
      MONGODB_URL: mongodb://mongodb:27017/up2d8
      JWT_SECRET_KEY: dev_secret_key_change_in_production
      # ... other env vars
    depends_on:
      - mongodb
    volumes:
      - ./backend:/app
    command: uvicorn api.main:app --host 0.0.0.0 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "5173:5173"
    environment:
      VITE_API_URL: http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev -- --host

volumes:
  mongodb_data:
```

#### Option 2: Manual (No Docker)

```bash
# Terminal 1: Start Ollama (for AI services)
ollama serve

# Terminal 2: Start MongoDB
mongod --dbpath ./data/mongodb
# Or use MongoDB Compass to manage local instance

# Terminal 3: Start Backend (FastAPI)
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --reload

# Terminal 4: Start Frontend (Vite + React)
cd frontend
npm install
npm run dev

# Services will be available at:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - MongoDB: mongodb://localhost:27017
```

### Run Tests
```bash
pytest backend/tests/unit/ -v           # Fast unit tests
pytest backend/tests/integration/ -v    # DB integration tests
pytest --cov=api                        # With coverage
```

### Check Code Quality
```bash
black backend/                          # Format
ruff backend/                           # Lint
mypy backend/                           # Type check
```

### Common Issues

**Docker Issues**:
- Port already in use → `docker-compose down` or kill process on port
- MongoDB won't start → Check Docker Desktop is running, try `docker-compose down -v` to remove volumes
- Backend won't build → Check Dockerfile.local exists, review build logs
- Changes not reflecting → Rebuild with `docker-compose up --build`

**MongoDB Issues**:
- Connection refused → Ensure MongoDB is running (Docker or local)
- Authentication failed → Check MONGODB_URL in environment
- Database not found → MongoDB auto-creates databases on first write
- Slow queries → Add indexes (see Database Changes section)

**Backend Issues**:
- Import errors → `pip install -r requirements.txt` in venv
- Ollama not responding → `ollama serve` (if using local LLM)
- JWT errors → Check JWT_SECRET_KEY is set in environment
- Port 8000 in use → Change port or kill process: `lsof -ti:8000 | xargs kill -9`

**Frontend Issues**:
- Vite won't start → `npm install` and check node version (18+)
- API calls failing → Check VITE_API_URL points to backend
- CORS errors → Backend must allow frontend origin in CORS middleware
- Port 5173 in use → Change port in vite.config.ts

**Data Issues**:
- ChromaDB errors → `rm -rf ./data/chroma` and restart
- Lost data → Check Docker volumes: `docker volume ls`
- Reset database → `docker-compose down -v` (WARNING: deletes all data)

---

## MongoDB Database Guide

### Overview

UP2D8 uses **MongoDB** as its primary database:
- **Local Development**: MongoDB 7 via Docker (`mongo:7` image)
- **Production**: Azure Cosmos DB with MongoDB API (free tier: 1000 RU/s, 25GB)

### Database Structure

```
up2d8 (database)
├── users                    # User accounts
├── user_preferences         # User settings & interests
├── articles                 # Scraped articles
├── digests                  # Generated daily digests
├── chat_messages           # Chat history
├── embeddings              # Article embeddings (optional, may use ChromaDB)
└── revoked_tokens          # Blacklisted JWT tokens (future)
```

### Collections Schema (Document Structure)

**users**:
```json
{
  "_id": "uuid-string",
  "email": "user@example.com",
  "password_hash": "bcrypt-hash",
  "full_name": "John Doe",
  "tier": "free",  // "free" | "pro" | "enterprise"
  "status": "active",  // "active" | "paused" | "suspended" | "deleted"
  "onboarding_completed": false,
  "oauth_provider": null,  // "google" | "microsoft" | null
  "oauth_id": null,
  "created_at": ISODate("2025-10-30T12:00:00Z"),
  "last_login_at": ISODate("2025-10-30T12:00:00Z")
}
```

**user_preferences**:
```json
{
  "_id": "uuid-string",
  "user_id": "user-uuid",
  "industries": ["AI", "FinTech", "Healthcare"],
  "keywords": ["machine learning", "blockchain"],
  "sources": ["TechCrunch", "VentureBeat"],
  "digest_frequency": "daily",  // "daily" | "weekly"
  "digest_time": "08:00",
  "email_enabled": true,
  "created_at": ISODate("2025-10-30T12:00:00Z"),
  "updated_at": ISODate("2025-10-30T12:00:00Z")
}
```

**articles**:
```json
{
  "_id": "uuid-string",
  "url": "https://...",
  "title": "Article Title",
  "content": "Full article text...",
  "summary": "AI-generated summary...",
  "source": "TechCrunch",
  "author": "John Smith",
  "published_at": ISODate("2025-10-30T10:00:00Z"),
  "scraped_at": ISODate("2025-10-30T11:00:00Z"),
  "industries": ["AI", "FinTech"],
  "keywords": ["GPT-4", "LLM"],
  "embedding_id": "chroma-vector-id",
  "relevance_score": 0.95
}
```

### Connection Setup

**File**: `backend/api/db/mongodb.py`

```python
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os

# Async client (for FastAPI endpoints)
_async_client = None
_async_db = None

async def get_database():
    """Get async MongoDB database instance."""
    global _async_client, _async_db
    if _async_db is None:
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        _async_client = AsyncIOMotorClient(mongodb_url)
        _async_db = _async_client.up2d8
    return _async_db

async def close_database():
    """Close async MongoDB connection."""
    global _async_client
    if _async_client:
        _async_client.close()

# Sync client (for background workers/scripts)
def get_sync_database():
    """Get sync MongoDB database instance."""
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = MongoClient(mongodb_url)
    return client.up2d8
```

### Common Operations

**1. Insert Document**:
```python
from api.db.mongodb import get_database

db = await get_database()
result = await db.users.insert_one({
    "_id": str(uuid.uuid4()),
    "email": "user@example.com",
    "created_at": datetime.utcnow()
})
user_id = result.inserted_id
```

**2. Find Document**:
```python
# Find one
user = await db.users.find_one({"email": "user@example.com"})

# Find many
articles = await db.articles.find(
    {"industries": {"$in": ["AI", "FinTech"]}}
).to_list(length=100)

# Find with projection (select fields)
user = await db.users.find_one(
    {"email": "user@example.com"},
    {"password_hash": 0}  # Exclude password
)
```

**3. Update Document**:
```python
# Update one
result = await db.users.update_one(
    {"_id": user_id},
    {"$set": {"last_login_at": datetime.utcnow()}}
)

# Update many
result = await db.users.update_many(
    {"tier": "free"},
    {"$set": {"status": "active"}}
)

# Upsert (insert if not exists)
result = await db.user_preferences.update_one(
    {"user_id": user_id},
    {"$set": {"digest_frequency": "daily"}},
    upsert=True
)
```

**4. Delete Document**:
```python
# Delete one
result = await db.articles.delete_one({"_id": article_id})

# Delete many (soft delete pattern)
result = await db.users.update_many(
    {"status": "deleted"},
    {"$set": {"deleted_at": datetime.utcnow()}}
)
```

**5. Aggregation Pipeline**:
```python
# Get article count by industry
pipeline = [
    {"$unwind": "$industries"},
    {"$group": {
        "_id": "$industries",
        "count": {"$sum": 1}
    }},
    {"$sort": {"count": -1}}
]
results = await db.articles.aggregate(pipeline).to_list(length=100)
```

### Indexes

**Create indexes on startup** (`backend/api/main.py`):

```python
@app.on_event("startup")
async def create_indexes():
    db = await get_database()

    # Users
    await db.users.create_index("email", unique=True)
    await db.users.create_index("created_at")

    # User preferences
    await db.user_preferences.create_index("user_id", unique=True)

    # Articles
    await db.articles.create_index([("industries", 1), ("published_at", -1)])
    await db.articles.create_index("url", unique=True)
    await db.articles.create_index("scraped_at")

    # Digests
    await db.digests.create_index([("user_id", 1), ("created_at", -1)])

    # Chat messages
    await db.chat_messages.create_index([("user_id", 1), ("created_at", -1)])

    # TTL index for revoked tokens (auto-delete after expiry)
    await db.revoked_tokens.create_index(
        "expires_at",
        expireAfterSeconds=0
    )
```

### Data Validation (Optional)

Add JSON Schema validation in production:

```python
# Example: Enforce user schema
await db.command({
    "collMod": "users",
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["_id", "email", "password_hash", "created_at"],
            "properties": {
                "_id": {"bsonType": "string"},
                "email": {"bsonType": "string", "pattern": "^.+@.+$"},
                "password_hash": {"bsonType": "string"},
                "tier": {"enum": ["free", "pro", "enterprise"]},
                "status": {"enum": ["active", "paused", "suspended", "deleted"]}
            }
        }
    },
    "validationLevel": "moderate"  # "strict" | "moderate"
})
```

### Migration Patterns

**No Alembic needed!** MongoDB is schemaless. Migrations are Python scripts.

**Example**: Add `tier` field to existing users:

```python
# backend/scripts/migrations/001_add_user_tier.py
import asyncio
from api.db.mongodb import get_database

async def migrate():
    db = await get_database()

    # Find users without tier field
    result = await db.users.update_many(
        {"tier": {"$exists": False}},
        {"$set": {"tier": "free", "updated_at": datetime.utcnow()}}
    )

    print(f"Updated {result.modified_count} users")

if __name__ == "__main__":
    asyncio.run(migrate())
```

**Run migration**:
```bash
cd backend
python scripts/migrations/001_add_user_tier.py
```

### Azure Cosmos DB Specifics

**Connection String Format**:
```
mongodb://your-account:PRIMARY_KEY@your-account.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@your-account@
```

**Important Notes**:
- Cosmos DB uses **Request Units (RU/s)** instead of raw performance
- Free tier: 1000 RU/s shared across all operations
- Optimize queries to use indexes (lower RU cost)
- Use `retrywrites=false` in connection string (Cosmos limitation)
- Monitor RU consumption in Azure Portal
- Consider **server-side pagination** for large result sets:
  ```python
  # Paginate with skip/limit (not efficient for large skips)
  page = 1
  limit = 20
  skip = (page - 1) * limit
  results = await db.articles.find().skip(skip).limit(limit).to_list(limit)

  # Better: Use cursor-based pagination
  last_id = request.query_params.get("last_id")
  query = {"_id": {"$gt": last_id}} if last_id else {}
  results = await db.articles.find(query).limit(20).to_list(20)
  ```

### Best Practices

1. **Always use indexes** for queried fields
2. **Use projections** to limit returned fields
3. **Batch operations** when possible (`insert_many`, `bulk_write`)
4. **Handle connection errors** with retry logic
5. **Use TTL indexes** for auto-expiring data (tokens, sessions)
6. **Validate data** with Pydantic before inserting
7. **Monitor query performance** in development
8. **Use async client (Motor)** for FastAPI, sync for scripts

---

## Authentication System

### Overview

UP2D8 uses **JWT-based authentication** with access and refresh tokens. The auth system is fully implemented and tested.

### Architecture

**Location**:
- Models: `backend/api/models/user.py`
- Utilities: `backend/api/utils/auth.py`
- Router: `backend/api/routers/auth.py`
- Database Models: `backend/api/db/models.py` (User, UserPreference tables)

**Token Strategy**:
- **Access Token**: Short-lived (15 minutes), used for API requests
- **Refresh Token**: Long-lived (7 days), used to get new access tokens
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Storage**: Tokens are stateless JWT, no server-side storage (MVP)

### API Endpoints

```
POST /api/v1/auth/signup       - Register new user
POST /api/v1/auth/login        - Authenticate user
POST /api/v1/auth/refresh      - Refresh access token
POST /api/v1/auth/logout       - Logout (validates token)
GET  /api/v1/auth/me           - Get current user info
```

### How to Use Authentication

#### 1. Protecting Routes

Use the `get_current_user` dependency to protect any route:

```python
from fastapi import APIRouter, Depends
from api.utils.auth import get_current_user
from api.db.models import User

router = APIRouter()

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.id, "email": current_user.email}
```

#### 2. Testing with curl

```bash
# 1. Signup
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!","full_name":"Test User"}'

# Response includes: user, access_token, refresh_token

# 2. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'

# 3. Access Protected Route
ACCESS_TOKEN="your_access_token_here"
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# 4. Refresh Token
REFRESH_TOKEN="your_refresh_token_here"
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\":\"$REFRESH_TOKEN\"}"
```

#### 3. Frontend Integration Example

```javascript
// Login
const response = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});
const { access_token, refresh_token, user } = await response.json();

// Store tokens (localStorage, sessionStorage, or memory)
localStorage.setItem('access_token', access_token);
localStorage.setItem('refresh_token', refresh_token);

// Access protected route
const protectedResponse = await fetch('http://localhost:8000/api/v1/articles', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});
```

### Password Security

**BCrypt Configuration**:
- Algorithm: BCrypt (via passlib)
- Rounds: Default (12 rounds)
- **Important**: BCrypt has a 72-byte limit on password length
- Passwords are automatically truncated to 72 bytes in `hash_password()` and `verify_password()`
- Pin bcrypt version to `4.0.1` for passlib compatibility (see backend/requirements.txt:54)

**Password Validation**:
- Minimum length: 12 characters
- Maximum length: 72 bytes (BCrypt limit)
- Validated via Pydantic in `UserCreate` model

### User Model Fields

```python
# Core fields (required)
id: UUID (auto-generated)
email: EmailStr (unique, indexed)
password_hash: str (BCrypt hashed)
full_name: str

# Status fields
tier: "free" | "pro" | "enterprise"
status: "active" | "paused" | "suspended" | "deleted"
onboarding_completed: bool

# Timestamps
created_at: datetime
last_login_at: datetime (nullable)
```

### Token Payload Structure

**Access Token**:
```json
{
  "sub": "user_id_uuid",
  "exp": 1234567890,
  "iat": 1234567890,
  "type": "access"
}
```

**Refresh Token**:
```json
{
  "sub": "user_id_uuid",
  "exp": 1234567890,
  "iat": 1234567890,
  "type": "refresh"
}
```

### Environment Variables

Required in `docker-compose.yml` and `.env` files:

```bash
JWT_SECRET_KEY=dev_secret_key_change_in_production_...  # Min 32 chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Common Auth Tasks

**Check if user is authenticated**:
```python
current_user: User = Depends(get_current_user)
# Automatically raises 401 if token invalid/expired
```

**Check user status**:
```python
if current_user.status != "active":
    raise HTTPException(status_code=403, detail="Account not active")
```

**Get user preferences (MongoDB)**:
```python
# Using Motor (async)
from api.db.mongodb import get_database

db = await get_database()
preferences = await db.user_preferences.find_one(
    {"user_id": current_user.id}
)

# Using PyMongo (sync)
from api.db.mongodb import get_sync_database

db = get_sync_database()
preferences = db.user_preferences.find_one(
    {"user_id": current_user.id}
)
```

**Manually decode token** (advanced):
```python
from api.utils.auth import decode_token

payload = decode_token(token_string)
user_id = payload.get("sub")
token_type = payload.get("type")  # "access" or "refresh"
```

### Important Notes for Future Development

1. **Token Blacklist**: Currently not implemented. For production, consider:
   - MongoDB-based token blacklist (simpler, no Redis needed)
   - Store revoked tokens in `revoked_tokens` collection
   - Add TTL index to auto-expire old tokens
   - Example:
     ```python
     # Add to revoked_tokens collection
     await db.revoked_tokens.insert_one({
         "token": token_hash,
         "revoked_at": datetime.utcnow(),
         "expires_at": datetime.utcnow() + timedelta(days=7)
     })
     # Create TTL index
     db.revoked_tokens.create_index("expires_at", expireAfterSeconds=0)
     ```

2. **Password Reset**: Not yet implemented. Will need:
   - POST /auth/forgot-password (send email with reset link)
   - POST /auth/reset-password (verify token, update password)

3. **Email Verification**: Not yet implemented. Consider adding:
   - `email_verified: bool` field to User model
   - Verification token generation
   - Email verification endpoint

4. **OAuth Integration**: Not yet implemented. Placeholder in User model:
   - `oauth_provider: str (nullable)`
   - `oauth_id: str (nullable)`

5. **Rate Limiting**: Consider adding rate limiting to auth endpoints to prevent brute force attacks.

6. **Security Best Practices**:
   - Never log passwords or tokens
   - Always use HTTPS in production
   - Rotate JWT_SECRET_KEY periodically
   - Set secure cookie flags if using cookies
   - Implement CORS properly (already done)

### Troubleshooting

**Issue**: "JWT_SECRET_KEY environment variable must be set"
- **Fix**: Add to docker-compose.yml environment section

**Issue**: "password cannot be longer than 72 bytes"
- **Fix**: Already handled in hash_password() and verify_password() functions
- BCrypt version must be pinned to 4.0.1 (ChromaDB conflict)

**Issue**: Token expired (401)
- **Fix**: Use refresh token to get new access token via POST /auth/refresh

**Issue**: "User not found" (401)
- **Fix**: User may have been deleted, or token contains invalid user_id

---

## Status Tracking

**Current Phase**: Week 1 - Database & Auth Complete ✅
**Next Milestone**: Week 3 - Content Scraping
**Target**: Week 8 - Backend MVP Complete

**Key Docs**:
- MVP Timeline: `docs/planning/mvp-roadmap.md`
- Setup Guide: `DEVELOPMENT_SETUP.md`
- Architecture: `docs/architecture/overview.md`
- **Conversational AI Agent (Planned for Weeks 10-11)**: `docs/architecture/conversational-ai-agent.md`

**Completed Features**:
- ✅ MongoDB database setup with Docker
- ✅ JWT authentication (signup, login, refresh, protected routes)
- ✅ User management with BCrypt password hashing
- ✅ Request logging middleware
- ✅ Docker Compose development environment

**Planned Features (Documented)**:
- 📋 Conversational AI Agent with LangChain/LangGraph (Weeks 10-11)
  - 3-layer memory system (digest context, short-term, long-term)
  - RAG over user article history
  - Web search integration (Brave Search API)
  - Link extraction and embedding
  - Streaming WebSocket responses with citations

---

**Last Updated**: 2025-10-30
**Project**: UP2D8
**Stack**: Python (FastAPI), MongoDB, Motor/PyMongo, Azure Web App (Backend), Azure Static Web Apps (Frontend), Azure Cosmos DB (MongoDB API), Ollama, ChromaDB
**Architecture**: MongoDB + Azure Free Tier
