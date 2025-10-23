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

## Status Tracking

**Current Phase**: Week 0 - Setup Complete ✅
**Next Milestone**: Week 1 - Database & Auth
**Target**: Week 8 - Backend MVP Complete

**Key Docs**:
- MVP Timeline: `docs/planning/mvp-roadmap.md`
- Setup Guide: `DEVELOPMENT_SETUP.md`
- Architecture: `docs/architecture/overview.md`

---

**Last Updated**: 2025-10-23
**Project**: UP2D8
**Stack**: Python (FastAPI), PostgreSQL, Redis, Ollama, ChromaDB
