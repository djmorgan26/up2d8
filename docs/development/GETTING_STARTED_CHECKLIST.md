# Getting Started Checklist

Use this checklist to get InsightStream running on your machine in ~30 minutes.

## ☑️ Pre-Flight Checklist

### System Requirements
- [ ] **Python 3.11+** installed
  ```bash
  python3 --version  # Should show 3.11 or higher
  ```

- [ ] **Node.js 18+** and npm installed
  ```bash
  node --version  # Should show 18.x or higher
  npm --version
  ```

- [ ] **Docker & Docker Compose** installed
  ```bash
  docker --version
  docker-compose --version
  ```

- [ ] **Git** installed
  ```bash
  git --version
  ```

---

## 🚀 Step 1: Install Ollama (5 minutes)

Ollama provides free, local LLM inference.

### Mac
- [ ] Install via Homebrew:
  ```bash
  brew install ollama
  ```

### Linux
- [ ] Install via script:
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```

### Windows
- [ ] Download installer from https://ollama.com/download
- [ ] Run the installer

### All Platforms
- [ ] Start Ollama service:
  ```bash
  ollama serve
  ```

  > **Note**: Leave this terminal running! Open a new terminal for next steps.

- [ ] Download a model (in a new terminal):
  ```bash
  ollama pull llama3.2:3b
  ```

  > This downloads ~2GB. It's a one-time download.

- [ ] Test it works:
  ```bash
  ollama run llama3.2:3b "Say hello!"
  ```

  You should see a response from the model.

**Status**: Ollama is running ✅

---

## 📦 Step 2: Clone & Setup Project (5 minutes)

- [ ] Clone the repository:
  ```bash
  git clone <your-repo-url>
  cd up2d8
  ```

- [ ] Create environment file:
  ```bash
  cp .env.example .env
  ```

  > **Note**: No need to edit `.env` for development! Defaults work out of the box.

- [ ] Create data directory:
  ```bash
  mkdir -p data/chroma
  ```

**Status**: Project files ready ✅

---

## 🐳 Step 3: Start Docker Services (3 minutes)

- [ ] Start PostgreSQL and Redis:
  ```bash
  docker-compose up -d
  ```

- [ ] Verify services are running:
  ```bash
  docker-compose ps
  ```

  You should see:
  - `insightstream-postgres` - healthy
  - `insightstream-redis` - healthy

- [ ] Test database connection:
  ```bash
  docker-compose exec postgres psql -U insightstream -c "SELECT 1"
  ```

  Should return `1`.

**Status**: Docker services running ✅

---

## 🐍 Step 4: Setup Python Backend (10 minutes)

- [ ] Navigate to backend:
  ```bash
  cd backend
  ```

- [ ] Create virtual environment:
  ```bash
  python3.11 -m venv venv
  ```

- [ ] Activate virtual environment:

  **Mac/Linux:**
  ```bash
  source venv/bin/activate
  ```

  **Windows:**
  ```bash
  venv\Scripts\activate
  ```

  Your prompt should now show `(venv)`.

- [ ] Upgrade pip:
  ```bash
  pip install --upgrade pip
  ```

- [ ] Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

  > **Note**: First run downloads ML models (~100MB). Takes 5-10 minutes. Grab a coffee! ☕

- [ ] Verify installation:
  ```bash
  python -c "import fastapi; import sqlalchemy; import sentence_transformers; print('All imports OK!')"
  ```

**Status**: Python environment ready ✅

---

## 🗄️ Step 5: Setup Database (2 minutes)

- [ ] Initialize Alembic (if not already done):
  ```bash
  alembic init alembic
  ```

  > Skip if `alembic/` folder already exists.

- [ ] Run migrations:
  ```bash
  alembic upgrade head
  ```

  Should see: "Running upgrade -> xxxxx, initial schema"

- [ ] Verify tables created:
  ```bash
  docker-compose exec postgres psql -U insightstream -c "\dt"
  ```

  Should show tables: `users`, `articles`, `digests`, etc.

**Status**: Database initialized ✅

---

## 🚀 Step 6: Start API Server (1 minute)

- [ ] Start FastAPI development server:
  ```bash
  uvicorn api.main:app --reload --port 8000
  ```

- [ ] In a new terminal, test the health endpoint:
  ```bash
  curl http://localhost:8000/health
  ```

  Should return: `{"status": "healthy"}`

- [ ] Open API docs in browser:

  Navigate to: http://localhost:8000/docs

  You should see the interactive Swagger UI.

**Status**: API server running ✅

---

## 🧪 Step 7: Test LLM Integration (2 minutes)

- [ ] Test Ollama directly:
  ```bash
  curl http://localhost:11434/api/generate -d '{
    "model": "llama3.2:3b",
    "prompt": "Summarize: OpenAI released GPT-5",
    "stream": false
  }'
  ```

  Should return a JSON response with a summary.

- [ ] Test via your API (create a test script):

  Create `backend/test_llm.py`:
  ```python
  import asyncio
  from api.services.llm_provider import get_llm_client

  async def test():
      client = get_llm_client()
      result = await client.generate(
          "Summarize: OpenAI released GPT-5 with improved reasoning.",
          max_tokens=50
      )
      print(f"Result: {result}")

  asyncio.run(test())
  ```

  Run it:
  ```bash
  python test_llm.py
  ```

  Should print a summary.

**Status**: LLM integration working ✅

---

## 🎨 Step 8: Setup Frontend (Optional - 5 minutes)

Only if you want to work on the frontend now:

- [ ] Navigate to frontend:
  ```bash
  cd ../frontend  # or: cd /path/to/up2d8/frontend
  ```

- [ ] Install dependencies:
  ```bash
  npm install
  ```

- [ ] Start development server:
  ```bash
  npm run dev
  ```

- [ ] Open in browser:

  Navigate to: http://localhost:5173 (or URL shown in terminal)

**Status**: Frontend running ✅ (optional)

---

## ✅ Verification Checklist

Run through these to confirm everything works:

### Core Services
- [ ] Ollama responds: `curl http://localhost:11434/api/version`
- [ ] PostgreSQL running: `docker-compose ps postgres`
- [ ] Redis running: `docker-compose ps redis`
- [ ] API health check: `curl http://localhost:8000/health`

### Backend Functionality
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Database tables exist: Check with pgAdmin or psql
- [ ] LLM generates text: Run `test_llm.py`
- [ ] Embeddings work: Test with sentence-transformers
- [ ] ChromaDB accessible: Check `./data/chroma` folder exists

### Optional Components
- [ ] Frontend loads (if you set it up)
- [ ] Celery worker running (if you need background tasks)

---

## 🎉 Success!

If all checkboxes are ✅, you're ready to develop!

### What's Running:
- **Ollama**: http://localhost:11434 (LLM)
- **API**: http://localhost:8000 (Backend)
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Frontend**: http://localhost:5173 (if started)

### Next Steps:

1. **Read the documentation**:
   - `DEVELOPMENT_SETUP.md` - Detailed setup guide
   - `README.md` - Project overview
   - `FREE_TIER_SUMMARY.md` - Cost-free development strategy

2. **Start building**:
   - Follow the MVP roadmap: `startingDocs/mvp-roadmap.md`
   - Start with Week 1 tasks (authentication, database models)

3. **Test provider switching**:
   ```bash
   # Try different LLM providers
   LLM_PROVIDER=ollama uvicorn api.main:app --reload
   ```

---

## 🐛 Troubleshooting

### Ollama Not Responding
```bash
# Check if running
ps aux | grep ollama

# Restart
killall ollama
ollama serve
```

### Docker Services Won't Start
```bash
# Stop all containers
docker-compose down

# Remove volumes (CAUTION: deletes data)
docker-compose down -v

# Restart
docker-compose up -d
```

### Python Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check virtual environment is activated
which python  # Should show venv path
```

### Database Connection Failed
```bash
# Check PostgreSQL is running
docker-compose logs postgres

# Verify connection string in .env matches docker-compose.yml
```

### Port Already in Use
```bash
# Find process using port (e.g., 8000)
lsof -i :8000

# Kill it
kill -9 <PID>
```

---

## 📊 Development Checklist

Daily development workflow:

### Morning Startup
- [ ] `ollama serve` (if not running)
- [ ] `docker-compose up -d`
- [ ] `cd backend && source venv/bin/activate`
- [ ] `uvicorn api.main:app --reload`

### Before Committing
- [ ] Run tests: `pytest`
- [ ] Format code: `black .`
- [ ] Lint: `ruff .`
- [ ] Type check: `mypy .`

### Evening Shutdown
- [ ] Stop API: Ctrl+C
- [ ] Stop Docker: `docker-compose down`
- [ ] Ollama can keep running (optional)

---

## 💡 Pro Tips

1. **Use separate terminals**:
   - Terminal 1: Ollama serve
   - Terminal 2: API server
   - Terminal 3: Celery worker (when needed)
   - Terminal 4: Git commands

2. **Monitor logs**:
   ```bash
   # API logs (auto-displayed by uvicorn --reload)

   # Docker logs
   docker-compose logs -f postgres
   docker-compose logs -f redis
   ```

3. **Quick database reset** (development only):
   ```bash
   docker-compose down -v && docker-compose up -d
   alembic upgrade head
   ```

4. **Test API endpoints** with Swagger UI at http://localhost:8000/docs instead of curl

---

## 🎓 Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com
- **Ollama**: https://ollama.com/library
- **sentence-transformers**: https://www.sbert.net
- **ChromaDB**: https://docs.trychroma.com

---

**Ready to Build! 🚀**

Time to start implementing the MVP features from `startingDocs/mvp-roadmap.md`!
