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
   - Use test database (Docker)
   - Mock external APIs only (Ollama, email)
   - Run before PR merge

3. **E2E Tests** (`backend/tests/e2e/`):
   - Test complete user workflows
   - Use test database + Redis
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

**Frontend Development**: Start in Week 9 after backend is solid

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
# Use only when you see these set:
LLM_PROVIDER=ollama              # FREE - local
OLLAMA_MODEL=llama3.2:3b         # Fast, good quality
EMBEDDING_PROVIDER=sentence-transformers  # FREE - local
VECTOR_DB_PROVIDER=chroma        # FREE - local
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
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxx
EMBEDDING_PROVIDER=openai
VECTOR_DB_PROVIDER=pinecone
EMAIL_PROVIDER=ses
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
│   ├── models/              # Pydantic models
│   ├── services/            # Business logic
│   │   ├── llm_provider.py
│   │   ├── embeddings.py
│   │   ├── vector_db.py
│   │   ├── email_provider.py
│   │   ├── scraper.py
│   │   ├── summarizer.py
│   │   └── digest_generator.py
│   ├── db/                  # Database
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── session.py       # DB connection
│   │   └── migrations/      # Alembic
│   └── utils/
├── workers/                 # Celery tasks
│   ├── celery_app.py
│   └── tasks.py
├── tests/                   # All tests here
└── requirements.txt
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

# Third-party
from fastapi import FastAPI, Depends
from sqlalchemy import Column, String
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

### Database Changes

1. Modify `backend/api/db/models.py`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Review migration SQL
4. Test: `alembic upgrade head`
5. Update `docs/architecture/data-models.md`

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
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start Docker (includes FastAPI)
docker-compose up -d

# FastAPI now runs in Docker at http://localhost:8000
# API docs: http://localhost:8000/docs
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
- Ollama not responding → `ollama serve`
- DB connection failed → `docker-compose up -d postgres`
- Import errors → `pip install -r requirements.txt`
- ChromaDB errors → `rm -rf ./data/chroma`

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

**Get user preferences**:
```python
preferences = db.query(UserPreference).filter(
    UserPreference.user_id == current_user.id
).first()
```

**Manually decode token** (advanced):
```python
from api.utils.auth import decode_token

payload = decode_token(token_string)
user_id = payload.get("sub")
token_type = payload.get("type")  # "access" or "refresh"
```

### Important Notes for Future Development

1. **Token Blacklist**: Currently not implemented. For production, implement Redis-based token blacklist for logout.

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
- ✅ Database schema with Alembic migrations
- ✅ JWT authentication (signup, login, refresh, protected routes)
- ✅ User management with BCrypt password hashing
- ✅ Request logging middleware

**Planned Features (Documented)**:
- 📋 Conversational AI Agent with LangChain/LangGraph (Weeks 10-11)
  - 3-layer memory system (digest context, short-term, long-term)
  - RAG over user article history
  - Web search integration (Brave Search API)
  - Link extraction and embedding
  - Streaming WebSocket responses with citations

---

**Last Updated**: 2025-10-24
**Project**: UP2D8
**Stack**: Python (FastAPI), PostgreSQL, Redis, Ollama, ChromaDB
