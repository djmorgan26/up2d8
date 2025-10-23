# UP2D8 (up2d8)

> AI-Powered Industry Insight Platform - Stay informed without information overload

[![Development Status](https://img.shields.io/badge/status-in%20development-yellow)]()
[![License](https://img.shields.io/badge/license-proprietary-red)]()

## 🎯 What is UP2D8?

UP2D8 delivers personalized daily AI digests about companies, industries, and technologies that matter to you. It combines:

- **Proactive Intelligence**: Daily email digests with AI-summarized industry news
- **Reactive Understanding**: Conversational AI assistant for deeper exploration
- **Personalized Curation**: Content ranked and filtered based on your interests

**Target Users**: Tech professionals, AI researchers, investment analysts, and career transitioners

---

## ✨ Key Features (MVP)

- ✅ **5 Pre-selected Companies**: OpenAI, Anthropic, Google AI, Microsoft, NVIDIA
- ✅ **Daily Email Digests**: Delivered at your preferred time (8 AM default)
- ✅ **AI Summarization**: Micro, standard, and detailed summaries
- ✅ **Contextual Chat**: Ask follow-up questions powered by RAG
- ✅ **Web Dashboard**: Browse past digests and bookmarked articles
- ✅ **Free Tier**: 100% free during development

---

## 🚀 Quick Start (Free Development)

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- [Ollama](https://ollama.com) (for free local LLM)

### 1. Install Ollama (Free Local AI)

**Mac:**
```bash
brew install ollama
ollama serve
ollama pull llama3.2:3b  # ~2GB download
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama pull llama3.2:3b
```

**Windows:** Download from [ollama.com/download](https://ollama.com/download)

### 2. Clone and Setup

```bash
git clone <your-repo-url>
cd up2d8

# Copy environment file
cp .env.development .env

# Start database services
docker-compose up -d

# Install Python dependencies
cd backend
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head
```

### 3. Start Development Servers

```bash
# Terminal 1 - API
cd backend
source venv/bin/activate
uvicorn api.main:app --reload --port 8000

# Terminal 2 - Worker (optional)
cd backend
source venv/bin/activate
celery -A workers.celery_app worker --loglevel=info

# Terminal 3 - Frontend (when ready)
cd frontend
npm install
npm run dev
```

### 4. Verify Setup

```bash
# Check API
curl http://localhost:8000/health

# Check Ollama
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:3b",
  "prompt": "Hello!",
  "stream": false
}'
```

**🎉 You're ready to develop!** Everything runs locally for **$0/month**.

For detailed setup instructions, see [DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md)

---

## 📁 Project Structure

```
up2d8/
├── .clauderc                      # Claude Code configuration ⭐
├── docker-compose.yml             # Local services (PostgreSQL, Redis)
├── .env.example                   # Environment template
├── PROJECT_STATUS.md              # Current status & next steps
│
├── backend/                       # Python FastAPI backend
│   ├── api/
│   │   ├── routers/              # API endpoints (TBD)
│   │   ├── models/               # Pydantic models (TBD)
│   │   ├── services/             # Business logic ⭐
│   │   │   ├── llm_provider.py       # Multi-provider LLM
│   │   │   ├── embeddings.py         # Embeddings abstraction
│   │   │   ├── vector_db.py          # Vector DB abstraction
│   │   │   └── email_provider.py     # Email abstraction
│   │   ├── db/                   # Database models (TBD)
│   │   └── utils/                # Utilities (TBD)
│   ├── workers/                  # Celery tasks (TBD)
│   ├── tests/                    # Comprehensive test suite ⭐
│   │   ├── unit/                # Fast, isolated tests
│   │   ├── integration/         # API & DB integration tests
│   │   ├── e2e/                 # End-to-end workflows
│   │   ├── fixtures/            # Test data
│   │   ├── conftest.py          # Pytest configuration
│   │   └── README.md            # Testing guide
│   ├── requirements.txt          # All dependencies
│   └── pytest.ini               # Pytest configuration
│
├── frontend/                     # React + TypeScript (Week 9+)
│   └── (To be implemented)
│
└── docs/                         # Organized documentation ⭐
    ├── README.md                # Documentation index
    ├── planning/                # Original requirements (READ-ONLY)
    │   ├── product-requirements.md
    │   ├── technical-architecture.md
    │   ├── mvp-roadmap.md
    │   └── database-api-spec.md
    ├── architecture/            # System design
    │   ├── overview.md
    │   └── services/           # Provider documentation
    ├── development/            # Setup & development guides
    │   ├── DEVELOPMENT_SETUP.md
    │   ├── FREE_TIER_SUMMARY.md
    │   └── GETTING_STARTED_CHECKLIST.md
    ├── features/               # Feature docs (TBD)
    ├── deployment/             # Production guides (TBD)
    └── decisions/              # Architecture Decision Records
        ├── 001-free-tier-development-strategy.md
        └── template.md
```

⭐ = Key files to review first

---

## 🔧 Technology Stack

### Development (FREE)
- **Backend**: FastAPI, SQLAlchemy, Celery
- **Database**: PostgreSQL (Docker), Redis (Docker)
- **LLM**: Ollama (llama3.2:3b) - local, free
- **Embeddings**: sentence-transformers - local, free
- **Vector DB**: ChromaDB - local, free
- **Email**: Console logs - free

### Production (Paid)
- **LLM**: Anthropic Claude Sonnet 4.5 (~$20/month)
- **Embeddings**: OpenAI text-embedding-3-small (~$5/month)
- **Vector DB**: Pinecone ($0-70/month)
- **Email**: AWS SES ($0.10 per 1,000 emails)
- **Infrastructure**: AWS ECS, RDS (~$30/month)

**No code changes needed to switch!** All configured via environment variables.

---

## 💰 Cost Breakdown

### Development: $0/month
- Everything runs locally
- No API keys required
- Perfect for learning and building

### Testing (Free Tiers): $0/month
- Groq API (free tier) for faster LLM
- Mailgun (5,000 emails/month free)
- Still using local DB and vector storage

### Production (100 users): ~$53/month
- LLM (Claude): ~$22.50/month
- Embeddings: ~$0.50/month
- Vector DB: $0/month (Pinecone free tier)
- Email: ~$0.30/month
- Infrastructure: ~$30/month

See [Development Setup](docs/development/DEVELOPMENT_SETUP.md) for detailed cost analysis.

---

## 📚 Documentation

### Essential Reading
- **[Project Status](PROJECT_STATUS.md)** - Current phase & next steps ⭐
- **[Development Setup](docs/development/DEVELOPMENT_SETUP.md)** - Free tier setup guide ⭐
- **[Getting Started Checklist](docs/development/GETTING_STARTED_CHECKLIST.md)** - Step-by-step setup ⭐
- **[Testing Guide](backend/tests/README.md)** - How to write and run tests ⭐

### Planning Documents
- **[Product Requirements](docs/planning/product-requirements.md)** - What we're building and why
- **[Technical Architecture](docs/planning/technical-architecture.md)** - System design and services
- **[MVP Roadmap](docs/planning/mvp-roadmap.md)** - 12-week implementation plan
- **[Database & API Specs](docs/planning/database-api-spec.md)** - Complete API reference

### All Documentation
- **[Documentation Index](docs/README.md)** - Complete guide to all docs

---

## 🎯 MVP Timeline (12 Weeks)

| Week | Phase | Deliverable |
|------|-------|-------------|
| 1-2 | Foundation | Database, Auth, Docker setup |
| 3-4 | Content Pipeline | Scraping, AI summarization |
| 5-7 | Digests | Email generation & delivery |
| 8-9 | Frontend | Dashboard & preferences UI |
| 10-11 | Chat | RAG system & chat interface |
| 12 | Launch | Testing, polish, 100 beta users |

Current Status: **Week 0 - Setup Complete** ✅

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Run specific test
pytest backend/tests/test_llm_provider.py -v

# Coverage report
pytest --cov=api --cov-report=html
```

---

## 🔐 Environment Configuration

### Development (.env.development)
```bash
# FREE - Local services only
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:3b
EMBEDDING_PROVIDER=sentence-transformers
VECTOR_DB_PROVIDER=chroma
EMAIL_PROVIDER=console
```

### Production (.env.production)
```bash
# PAID - Production services
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxx
EMBEDDING_PROVIDER=openai
VECTOR_DB_PROVIDER=pinecone
EMAIL_PROVIDER=ses
```

Copy the appropriate file to `.env` and customize.

---

## 🛠️ Development Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes with tests**
   ```bash
   # Write code
   # Write tests
   pytest  # Ensure tests pass
   ```

3. **Commit and push**
   ```bash
   git add .
   git commit -m "Add feature: description"
   git push origin feature/your-feature-name
   ```

4. **Create Pull Request**
   - CI/CD will run tests automatically
   - Get review from team
   - Merge to main

---

## 🚢 Deployment

### Staging (Auto-deploy from main)
```bash
# Push to main triggers auto-deploy to staging
git push origin main
```

### Production (Manual approval)
```bash
# Via GitHub Actions or AWS Console
# Requires manual approval from team lead
```

See `infrastructure/` for Terraform configs.

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

### Code Standards
- Python: Black, Ruff, mypy
- TypeScript: ESLint, Prettier
- Commit messages: Conventional Commits

---

## 🐛 Troubleshooting

### Common Issues

**Ollama not responding:**
```bash
ollama serve  # Make sure it's running
```

**Database connection failed:**
```bash
docker-compose up -d postgres
docker-compose logs postgres  # Check logs
```

**Import errors after pip install:**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**ChromaDB errors:**
```bash
rm -rf ./data/chroma  # Delete and recreate
```

See [DEVELOPMENT_SETUP.md#troubleshooting](DEVELOPMENT_SETUP.md#troubleshooting) for more.

---

## 📈 Roadmap

### ✅ Phase 0 (Current)
- [x] Project structure
- [x] Free tier configuration
- [x] Multi-provider abstraction
- [x] Development environment

### 🔄 Phase 1 (Week 1-2)
- [ ] Database migrations
- [ ] Authentication system
- [ ] Basic API structure

### 📅 Phase 2 (Week 3-4)
- [ ] Content scrapers
- [ ] AI summarization
- [ ] Classification pipeline

### 📅 Phase 3 (Week 5-7)
- [ ] Digest generation
- [ ] Email delivery
- [ ] Preferences management

See [MVP Roadmap](docs/planning/mvp-roadmap.md) for complete timeline.

---

## 📄 License

Proprietary - All rights reserved

---

## 📞 Contact & Support

- **Project Lead**: David Morgan
- **Repository**: [GitHub](https://github.com/yourusername/up2d8)
- **Issues**: [GitHub Issues](https://github.com/yourusername/up2d8/issues)

---

## 🙏 Acknowledgments

- Built with guidance from comprehensive planning documents
- Using free and open-source tools wherever possible
- Anthropic Claude for production LLM
- Ollama community for free local LLMs

---

**Ready to build?** Start with [DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md) 🚀
