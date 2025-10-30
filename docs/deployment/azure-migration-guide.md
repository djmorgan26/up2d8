# UP2D8 Azure Migration Guide
## FREE Tier Deployment to Azure Functions

This guide explains how to migrate UP2D8 from Docker/PostgreSQL to Azure Functions with Cosmos DB for **100% FREE** operation.

---

## What We've Changed

### 1. Database: PostgreSQL → Cosmos DB (MongoDB API)
- **Why**: Azure Cosmos DB free tier (1000 RU/s, 25 GB)
- **File**: `backend/api/db/cosmos_db.py`
- **Connection**: MongoDB driver (pymongo)

### 2. Cache: Redis → In-Memory Cache
- **Why**: No free Redis on Azure (not critical for MVP)
- **File**: `backend/api/utils/cache.py`
- **Limitation**: Data lost on restart, single instance only

### 3. LLM: Ollama → Groq
- **Why**: Groq has FREE tier (14,400 req/day, fast)
- **File**: `backend/api/services/groq_client.py`
- **API Key**: Already configured in `.env.azure`

### 4. Background Tasks: Celery → Azure Durable Functions
- **Why**: No free way to run Celery on Azure
- **Implementation**: Convert tasks to Durable Functions
- **Scheduled Tasks**: Use Timer Triggers (replaces Celery Beat)

---

## Azure Resources (All FREE)

| Resource | Free Tier | Purpose |
|----------|-----------|---------|
| Azure Functions (Consumption) | 1M requests/month | API + Background tasks |
| Azure Cosmos DB | 1000 RU/s + 25 GB | Database (MongoDB API) |
| Azure Blob Storage | 5 GB LRS | ChromaDB persistence |
| Groq API | 14,400 req/day | LLM (replaces Ollama) |

**Total Monthly Cost**: $0 (within free tiers)

---

## Configuration Files

### 1. `.env.azure`
Contains all your Azure credentials:
- Cosmos DB connection string
- Azure Storage connection string
- Groq API key
- Function App details

**IMPORTANT**: Never commit this file to Git! It's already in `.gitignore`.

### 2. `host.json`
Azure Functions runtime configuration:
- Timeout: 5 minutes
- Logging: Application Insights
- HTTP settings

---

## Migration Steps

### Step 1: Test Cosmos DB Connection

```bash
# Test Cosmos DB locally
cd backend
python3 -m api.db.cosmos_db
```

**Expected Output**:
```
✅ Connected to Cosmos DB: up2d8
Collections: []
✅ Indexes created
```

If you see errors:
- Check that `COSMOS_DB_CONNECTION_STRING` in `.env.azure` is correct
- Ensure Cosmos DB cluster is running in Azure Portal

### Step 2: Test Groq API

```bash
# Test Groq LLM
cd backend
export GROQ_API_KEY=your_groq_api_key_here
python3 -m api.services.groq_client
```

**Expected Output**:
```
=== Testing Generation ===
Response: AI benefits include...

=== Testing Chat ===
Chat Response: Why do programmers prefer dark mode?...

✅ All Groq tests passed!
```

### Step 3: Install Azure Functions Core Tools

```bash
# macOS
brew install azure-functions-core-tools@4

# Verify installation
func --version
```

### Step 4: Initialize Azure Functions Project

We need to convert the FastAPI app to Azure Functions. Here's what needs to happen:

1. Create `function_app.py` in project root (coming next)
2. Create HTTP triggers for each API endpoint
3. Create Timer triggers for scheduled tasks
4. Create Durable Functions for background tasks

---

## Architecture Comparison

### Before (Docker)
```
┌──────────────┐     ┌────────────┐     ┌───────────┐
│   FastAPI    │────▶│ PostgreSQL │     │   Redis   │
│   (API)      │     │   (DB)     │     │  (Cache)  │
└──────────────┘     └────────────┘     └───────────┘
        │
        ▼
┌──────────────┐     ┌────────────┐
│   Celery     │────▶│   Ollama   │
│  (Workers)   │     │   (LLM)    │
└──────────────┘     └────────────┘
```

### After (Azure)
```
┌─────────────────────────────────────┐
│     Azure Function App              │
│                                     │
│  ┌──────────────┐  ┌──────────────┐│
│  │ HTTP Triggers│  │Timer Triggers││
│  │   (API)      │  │  (Scheduled) ││
│  └──────────────┘  └──────────────┘│
│                                     │
│  ┌──────────────────────────────┐  │
│  │   Durable Functions          │  │
│  │   (Background Tasks)         │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
         │              │
         ▼              ▼
┌──────────────┐  ┌──────────────┐
│  Cosmos DB   │  │  Groq API    │
│  (MongoDB)   │  │  (LLM-FREE)  │
└──────────────┘  └──────────────┘
         │
         ▼
┌──────────────┐
│Azure Blob    │
│Storage       │
│(ChromaDB)    │
└──────────────┘
```

---

## What Needs to Be Done Next

### Task 1: Create Azure Functions HTTP Triggers
Convert FastAPI routes to Azure Function HTTP triggers.

**Example**:
```python
# OLD: backend/api/routers/auth.py
@router.post("/login")
async def login(credentials: LoginRequest):
    ...

# NEW: function_app.py
@app.route(route="auth/login", methods=["POST"])
async def login(req: func.HttpRequest):
    ...
```

### Task 2: Create Timer Triggers
Replace Celery Beat scheduled tasks with Timer Triggers.

**Example**:
```python
# OLD: Celery Beat schedule
@celery_app.task
def generate_daily_digests():
    ...

# NEW: Timer Trigger (runs daily at 6 AM)
@app.schedule(schedule="0 0 6 * * *", ...)
def generate_daily_digests(timer: func.TimerRequest):
    ...
```

### Task 3: Create Durable Functions
Replace Celery tasks with Durable Functions for long-running operations.

**Example**:
```python
# OLD: Celery task
@celery_app.task
def embed_article(article_id):
    ...

# NEW: Durable Function
@app.orchestration_trigger(...)
def embed_article_orchestrator(context):
    article_id = context.get_input()
    result = yield context.call_activity("embed_article_activity", article_id)
    return result
```

---

## Deployment Commands

Once everything is converted:

```bash
# 1. Build for deployment
cd /Users/davidmorgan/Documents/Repositories/up2d8
pip install -r backend/requirements.txt --target .python_packages/lib/site-packages

# 2. Login to Azure
az login

# 3. Deploy to Function App
func azure functionapp publish up2d8

# 4. Verify deployment
curl https://up2d8.azurewebsites.net/api/health
```

---

## Monitoring & Debugging

### View Logs
```bash
# Stream logs
func azure functionapp logstream up2d8

# Or in Azure Portal
# Function App → Monitor → Log Stream
```

### Check Cosmos DB
```bash
# In Azure Portal
# Cosmos DB → Data Explorer → Browse collections
```

### Monitor Groq Usage
- Dashboard: https://console.groq.com/
- Check daily request count (limit: 14,400/day)

---

## Cost Management

### Free Tier Limits

**Azure Functions (Consumption)**:
- 1,000,000 requests/month FREE
- 400,000 GB-s execution time FREE
- After that: ~$0.20 per million requests

**Cosmos DB**:
- 1000 RU/s + 25 GB FREE (forever)
- After that: ~$24/month per 100 RU/s

**Azure Storage**:
- 5 GB LRS hot storage FREE
- After that: ~$0.02 per GB

**Groq API**:
- 14,400 requests/day FREE
- No paid tier yet (may change)

### How to Stay FREE

1. **Limit scraping**: Max 20 articles per scrape
2. **Cache aggressively**: Reduce Cosmos DB queries
3. **Use Groq wisely**: Cache LLM responses
4. **Monitor usage**: Check Azure Portal weekly

---

## Troubleshooting

### Cosmos DB Connection Failed
```
Error: Authentication failed
```
**Fix**: Check `COSMOS_DB_CONNECTION_STRING` in `.env.azure` matches Azure Portal

### Groq API Rate Limit
```
Error: Rate limit exceeded
```
**Fix**: You've hit 14,400 req/day limit. Wait 24 hours or cache more aggressively.

### Function Timeout
```
Error: Function execution timeout
```
**Fix**: Long-running tasks need Durable Functions, not HTTP triggers

### Cold Start Slow
```
First request takes 5-10 seconds
```
**Fix**: This is normal for Consumption plan. Consider Premium plan later (not free).

---

## Next Steps

1. ✅ Cosmos DB abstraction layer created
2. ✅ In-memory cache created
3. ✅ Groq client created
4. ✅ Environment configuration created
5. ⏳ Convert Celery tasks to Durable Functions (NEXT)
6. ⏳ Create HTTP triggers for API endpoints
7. ⏳ Create Timer triggers for scheduled tasks
8. ⏳ Test deployment to Azure

---

## Support & Resources

- **Azure Functions Docs**: https://docs.microsoft.com/en-us/azure/azure-functions/
- **Cosmos DB Docs**: https://docs.microsoft.com/en-us/azure/cosmos-db/
- **Groq API Docs**: https://console.groq.com/docs/
- **Durable Functions**: https://docs.microsoft.com/en-us/azure/azure-functions/durable/

---

**Last Updated**: 2025-10-26
**Status**: Migration in progress
