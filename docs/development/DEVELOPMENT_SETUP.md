# Free-Tier Development Setup Guide

This guide shows you how to set up InsightStream for **completely free** local development, then migrate to paid services for production.

## 🎯 Cost Comparison

### Development (FREE)
- **LLM**: Ollama (local) - $0/month
- **Embeddings**: sentence-transformers (local) - $0/month
- **Vector DB**: ChromaDB (local) - $0/month
- **Email**: Console logs - $0/month
- **Database**: PostgreSQL (Docker) - $0/month
- **Redis**: Redis (Docker) - $0/month

**Total Monthly Cost: $0**

### Production (Starting ~$50/month)
- **LLM**: Anthropic Claude (~$20/month)
- **Embeddings**: OpenAI ($5/month)
- **Vector DB**: Pinecone ($0-70/month depending on scale)
- **Email**: AWS SES ($0.10 per 1,000 emails)
- **Infrastructure**: AWS ECS/RDS (~$30/month)

---

## 🚀 Quick Start (Free Local Development)

### Step 1: Install Ollama (Free Local LLM)

**Mac:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from https://ollama.com/download

**Start Ollama and download a model:**
```bash
# Start Ollama service
ollama serve

# In another terminal, download a model (choose one):
ollama pull llama3.2:3b      # 3B params - Fast, good for dev (recommended)
ollama pull mistral:7b       # 7B params - Better quality, slower
ollama pull phi3:mini        # 3.8B params - Very fast, Microsoft
```

**Test it:**
```bash
ollama run llama3.2:3b "Summarize: OpenAI released GPT-5 with improved reasoning capabilities and 50% faster inference."
```

### Step 2: Clone and Setup Project

```bash
# Clone repository
git clone <your-repo-url>
cd up2d8

# Copy development environment file
cp .env.development .env

# No need to add API keys for development!
```

### Step 3: Start Docker Services

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Verify they're running
docker-compose ps
```

### Step 4: Install Python Dependencies

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (this will download sentence-transformers models automatically)
pip install -r requirements.txt

# The first run will download ~100MB of ML models locally (one-time)
```

### Step 5: Run Database Migrations

```bash
# Create database tables
alembic upgrade head
```

### Step 6: Start Development Servers

```bash
# Terminal 1 - API Server
cd backend
source venv/bin/activate
uvicorn api.main:app --reload --port 8000

# Terminal 2 - Celery Worker (for background tasks)
cd backend
source venv/bin/activate
celery -A workers.celery_app worker --loglevel=info

# Terminal 3 - Frontend (when ready)
cd frontend
npm install
npm run dev
```

### Step 7: Test the Free Stack

```bash
# Test LLM (Ollama)
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:3b",
  "prompt": "Say hello!",
  "stream": false
}'

# Test API
curl http://localhost:8000/health
```

---

## 📦 What Gets Downloaded Automatically

When you first run the application, these models download automatically (one-time):

1. **sentence-transformers/all-MiniLM-L6-v2** (~80MB)
   - For embeddings/vector search
   - Runs on CPU, very fast

2. **ChromaDB** (~10MB)
   - Local vector database
   - No configuration needed

3. **Ollama models** (varies by model)
   - llama3.2:3b: ~2GB
   - mistral:7b: ~4GB
   - phi3:mini: ~2.3GB

**Total initial download: ~2-4GB depending on LLM choice**

---

## 💰 Free Tier API Options (When You're Ready)

### LLM APIs (All have free tiers)

**Groq (Recommended for Testing)**
- Free tier: Very generous
- Speed: Ultra-fast inference
- Models: Llama 3.1, Mixtral
- Sign up: https://console.groq.com
```bash
# Add to .env
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

**Together.ai**
- Free credits: $25
- Models: Many open-source models
- Sign up: https://together.ai
```bash
LLM_PROVIDER=together
TOGETHER_API_KEY=your_key_here
```

### Email Services (Free Tiers)

**Mailgun (Recommended)**
- Free: 5,000 emails/month for 3 months
- Then: First 1,000 emails/month free
- Sign up: https://www.mailgun.com
```bash
EMAIL_PROVIDER=mailgun
MAILGUN_API_KEY=your_key_here
MAILGUN_DOMAIN=mg.yourdomain.com
```

**Brevo (formerly Sendinblue)**
- Free: 300 emails/day (9,000/month)
- Sign up: https://www.brevo.com
```bash
EMAIL_PROVIDER=brevo
BREVO_API_KEY=your_key_here
```

**MailerSend**
- Free: 12,000 emails/month
- Sign up: https://www.mailersend.com
```bash
EMAIL_PROVIDER=mailersend
MAILERSEND_API_KEY=your_key_here
```

---

## 🔄 Switching Between Providers

All providers are configured via environment variables. Just change the .env file:

### Development → Groq (Free but requires signup)
```bash
# .env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_xxxxx
GROQ_MODEL=llama-3.1-8b-instant
```

### Development → Production (Anthropic)
```bash
# .env.production
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxx
LLM_MODEL=claude-sonnet-4.5
```

No code changes needed! The abstraction layer handles everything.

---

## 🧪 Testing Different Providers

Create a test script to compare providers:

```python
# test_providers.py
import asyncio
from api.services.llm_provider import LLMFactory
import os

async def test_llm():
    # Test current provider
    client = LLMFactory.create_client()

    prompt = """Summarize this in 2 sentences:
    OpenAI released GPT-5 with 50% faster inference and improved reasoning capabilities.
    The model is available via API starting today at $0.03 per 1K tokens.
    """

    result = await client.generate(prompt, max_tokens=100)
    print(f"Provider: {os.getenv('LLM_PROVIDER')}")
    print(f"Result: {result}\n")

asyncio.run(test_llm())
```

Run with different providers:
```bash
# Test Ollama (local, free)
LLM_PROVIDER=ollama python test_providers.py

# Test Groq (API, free tier)
LLM_PROVIDER=groq GROQ_API_KEY=xxx python test_providers.py
```

---

## 📊 Performance Comparison

Based on summarizing a 500-word article:

| Provider | Speed | Cost | Quality | Best For |
|----------|-------|------|---------|----------|
| Ollama (llama3.2:3b) | 2-3s | FREE | Good | Development |
| Ollama (mistral:7b) | 4-6s | FREE | Better | Development |
| Groq (llama-3.1-8b) | 0.5-1s | FREE tier | Good | Testing |
| Claude Sonnet 4.5 | 1-2s | $3/1M tokens | Excellent | Production |
| GPT-4o-mini | 1-2s | $0.15/1M tokens | Very Good | Production |

---

## 🎓 Learning Path

**Week 1: Local Development (Free)**
- Use Ollama + ChromaDB + Console email
- Learn how the system works
- Build core features

**Week 2-3: Free Tier APIs (Still Free)**
- Add Groq API key for faster LLM
- Add Mailgun for real email testing
- Test with 10-20 users

**Week 4+: Production Ready**
- Migrate to Anthropic/OpenAI for quality
- Use Pinecone for scale
- Deploy to AWS

---

## 🐛 Troubleshooting

### Ollama not responding
```bash
# Check if Ollama is running
ps aux | grep ollama

# Restart Ollama
killall ollama
ollama serve
```

### sentence-transformers download fails
```bash
# Pre-download the model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### ChromaDB errors
```bash
# Clear ChromaDB data
rm -rf ./data/chroma
# It will recreate on next run
```

### Out of memory with Ollama
```bash
# Use a smaller model
ollama pull llama3.2:3b  # Instead of 7b or larger
```

---

## 💡 Pro Tips

1. **Start with llama3.2:3b** - It's fast enough for development and won't eat your RAM

2. **Use console email in dev** - See emails in terminal, no external service needed

3. **ChromaDB is perfect for dev** - No setup, works immediately, data stored locally

4. **Cache aggressively** - Set `USE_CACHE_AGGRESSIVELY=true` to avoid re-processing

5. **Limit scraping in dev** - Set `MAX_ARTICLES_PER_SCRAPE=10` to keep data small

6. **Test prompts locally first** - Iterate on prompts with Ollama before using paid APIs

---

## 🚀 When to Upgrade to Paid Services

**Stay Free If:**
- ✅ Building MVP
- ✅ Learning the system
- ✅ < 10 test users
- ✅ Response time 2-3s is OK

**Upgrade When:**
- 📈 > 50 active users
- 📈 Need sub-second responses
- 📈 Summary quality matters for UX
- 📈 Email deliverability is critical
- 📈 Raising money / going to production

---

## 📝 Cost Estimation for Production

**For 100 active users:**
- 100 digests/day × 5 articles = 500 summaries/day
- 500 summaries × ~500 tokens = 250K tokens/day
- 250K tokens × $3/1M = **$0.75/day** = **$22.50/month** (LLM)
- Email (100/day): **$0.30/month**
- Vector DB (Pinecone starter): **$0/month** (free tier)
- Infrastructure (AWS): **~$30/month**

**Total: ~$53/month for 100 users**

---

## 🎯 Next Steps

1. ✅ Set up Ollama
2. ✅ Run `docker-compose up`
3. ✅ Install Python dependencies
4. ✅ Start API server
5. ✅ Test with `/health` endpoint
6. ✅ Build your first feature!

**Questions?** Check the main README.md or technical architecture docs.

**Ready to build?** The entire stack is now running locally for $0/month! 🎉
