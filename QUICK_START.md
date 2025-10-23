# UP2D8 - Quick Start Guide

**Get up and running in 15 minutes** ⚡

---

## 🎯 What You'll Get

- ✅ Complete backend development environment
- ✅ 100% free local services (Ollama, ChromaDB, PostgreSQL, Redis)
- ✅ Zero API keys needed
- ✅ Ready to start coding

---

## ⚡ Quick Start (3 Steps)

### Step 1: Install Ollama (5 min)

**Mac:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:** Download from [ollama.com/download](https://ollama.com/download)

**Then:**
```bash
# Start Ollama (keep this running)
ollama serve

# In a new terminal, download model
ollama pull llama3.2:3b
```

### Step 2: Start Services (2 min)

```bash
# Clone and setup
git clone <your-repo-url>
cd up2d8
cp .env.example .env

# Start PostgreSQL and Redis
docker-compose up -d
```

### Step 3: Install Python & Test (8 min)

```bash
# Create environment
cd backend
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies (first run downloads ML models ~100MB)
pip install -r requirements.txt

# Test it works
pytest tests/unit/test_llm_provider.py -v
```

---

## ✅ Verify Setup

```bash
# Check services
curl http://localhost:11434/api/version        # Ollama
docker-compose ps                               # PostgreSQL & Redis

# Run test suite
pytest tests/unit/ -v                           # Should pass!
```

**All green?** You're ready! 🎉

---

## 🚀 Start Developing

```bash
# Terminal 1: API Server
cd backend
source venv/bin/activate
uvicorn api.main:app --reload

# Terminal 2: Watch Tests
pytest tests/unit/ -v --watch  # (if pytest-watch installed)
```

Visit:
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

---

## 📖 Next Steps

1. **Read Project Status**: [PROJECT_STATUS.md](PROJECT_STATUS.md)
2. **Review Week 1 Tasks**: [MVP Roadmap](docs/planning/mvp-roadmap.md)
3. **Understand Architecture**: [Architecture Overview](docs/architecture/overview.md)
4. **Write Your First Test**: [Testing Guide](backend/tests/README.md)

---

## 🎓 Key Concepts

### Provider Abstraction
Everything uses FREE local services by default:
- **LLM**: Ollama (not Claude)
- **Embeddings**: sentence-transformers (not OpenAI)
- **Vector DB**: ChromaDB (not Pinecone)
- **Email**: Console logs (not AWS SES)

Switch to paid services later by just changing `.env`!

### Backend-First Development
Build backend first (Weeks 1-8), frontend later (Weeks 9-12).

### Test-Driven Development
Write tests as you code. Aim for > 80% coverage.

---

## 🆘 Troubleshooting

**Ollama not responding?**
```bash
ollama serve  # Make sure it's running
```

**Docker won't start?**
```bash
docker-compose down
docker-compose up -d
```

**Import errors?**
```bash
pip install -r requirements.txt --force-reinstall
```

**Still stuck?** Check [Troubleshooting Guide](docs/development/GETTING_STARTED_CHECKLIST.md#troubleshooting)

---

## 💡 Development Workflow

```bash
# Daily startup
ollama serve                          # Terminal 1 (keep running)
docker-compose up -d                  # Start DB & Redis
cd backend && source venv/bin/activate
uvicorn api.main:app --reload        # Terminal 2

# Before committing
pytest                                # Run tests
black backend/                        # Format code
ruff backend/                         # Lint
```

---

## 📊 Cost Tracker

**Current Cost**: $0/month 💰

**What's Free**:
- Ollama (local LLM)
- sentence-transformers (local embeddings)
- ChromaDB (local vector DB)
- PostgreSQL (Docker)
- Redis (Docker)
- All development tools

**When to Upgrade**: Only when launching to 50+ real users (Week 11-12+)

---

## 📚 Essential Reading

**Today**:
- [x] This file (you're here!)
- [ ] [PROJECT_STATUS.md](PROJECT_STATUS.md) (5 min)
- [ ] [Free Tier Summary](docs/development/FREE_TIER_SUMMARY.md) (10 min)

**This Week**:
- [ ] [MVP Roadmap](docs/planning/mvp-roadmap.md) - Week 1 section
- [ ] [Database & API Specs](docs/planning/database-api-spec.md) - Database schema
- [ ] [Testing Guide](backend/tests/README.md)

---

## 🎯 Your First Task

Build the authentication system (Week 1):

1. Create database models (`backend/api/db/models.py`)
2. Set up Alembic migrations
3. Implement `/auth/signup` endpoint
4. Write tests for signup flow
5. Document in `docs/features/authentication.md`

**Need help?** Check [.clauderc](.clauderc) for detailed guidelines!

---

**Time to Start**: ~15 minutes
**Cost**: $0
**Difficulty**: Easy (everything is set up!)

**Ready to build?** 🚀

```bash
cd backend
source venv/bin/activate
# Start coding!
```
