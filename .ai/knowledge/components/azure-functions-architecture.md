---
type: component
name: Azure Functions Architecture
status: implemented
created: 2025-11-08
updated: 2025-11-08
files:
  - packages/functions/NewsletterGenerator/__init__.py
  - packages/functions/CrawlerOrchestrator/__init__.py
  - packages/functions/CrawlerWorker/__init__.py
  - packages/functions/DataArchival/__init__.py
  - packages/functions/HealthMonitor/__init__.py
  - packages/functions/ManualTrigger/__init__.py
  - packages/functions/shared/
related:
  - ../patterns/azure-functions-local-dev.md
tags: [azure-functions, serverless, background-tasks, python, timer-triggers, queue-triggers]
---

# Azure Functions Architecture

## What It Does

Provides serverless background task processing for the UP2D8 platform. Handles scheduled operations (RSS feed scraping, newsletter generation, data archival), asynchronous web crawling with durable orchestrations, and system health monitoring. Functions run independently from the main Backend API, triggered by timers, queues, or HTTP requests.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Azure Functions                       │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Timer Trig   │  │ Queue Trig   │  │ HTTP Trig    │ │
│  │              │  │              │  │              │ │
│  │ Newsletter   │  │ Crawler      │  │ Manual       │ │
│  │ Generator    │  │ Worker       │  │ Trigger      │ │
│  │              │  │              │  │              │ │
│  │ Health       │  │              │  │ Crawler      │ │
│  │ Monitor      │  │              │  │ Orchestrator │ │
│  │              │  │              │  │              │ │
│  │ Data         │  │              │  │              │ │
│  │ Archival     │  │              │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │          Shared Services                         │  │
│  │                                                  │  │
│  │  - email_service.py     (SendGrid/Brevo SMTP)  │  │
│  │  - backend_client.py    (FastAPI REST client)   │  │
│  │  - key_vault_client.py  (Azure Key Vault)       │  │
│  │  - logger_config.py     (Structlog setup)       │  │
│  │  - orchestration_logic.py (Durable Functions)   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
         │                    │                   │
         ▼                    ▼                   ▼
   ┌──────────┐      ┌──────────────┐     ┌──────────┐
   │ Cosmos   │      │ Azure Queue  │     │ SendGrid │
   │ DB       │      │ Storage      │     │ (Email)  │
   └──────────┘      └──────────────┘     └──────────┘
```

## Functions Catalog

### 1. NewsletterGenerator (Timer Trigger)

**Purpose**: Generates and sends personalized daily newsletters to users with curated articles.

**Schedule**: Timer trigger (configured in `function.json`)

**Flow**:
1. Connects to Cosmos DB (MongoDB API)
2. Fetches users with `receiveDailyNewsletter: true`
3. For each user:
   - Fetches recent articles from `articles` collection
   - Uses Google Gemini API to generate personalized summary
   - Converts markdown summary to HTML
   - Sends email via Brevo SMTP
4. Logs completion status

**Key dependencies**:
- `pymongo` - Cosmos DB access
- `google-generativeai` - Gemini AI for summaries
- `markdown` - Markdown to HTML conversion
- `shared.email_service.SMTPProvider` - Email delivery

**Configuration**:
- `COSMOS-DB-CONNECTION-STRING-UP2D8` (Key Vault)
- `UP2D8-GEMINI-API-Key` (Key Vault)
- `UP2D8-SMTP-KEY` (Key Vault)
- `BREVO_SMTP_HOST`, `BREVO_SMTP_PORT`, `SENDER_EMAIL` (environment)

**File**: `packages/functions/NewsletterGenerator/__init__.py:1`

### 2. CrawlerOrchestrator (HTTP + Durable Functions)

**Purpose**: Orchestrates multi-step web crawling workflows using durable functions pattern.

**Trigger**: HTTP request (POST/GET to `/api/CrawlerOrchestrator`)

**Flow** (Durable Orchestration):
1. Receives crawl request with URL
2. Starts orchestration instance
3. Schedules parallel crawl activities
4. Aggregates results
5. Stores in Cosmos DB
6. Returns orchestration status

**Durable Functions Features**:
- Checkpointing - Restarts from last successful step on failure
- Fan-out/fan-in - Parallel crawling of multiple URLs
- Long-running - Can execute for hours/days

**Dependencies**:
- `shared.orchestration_logic` - Orchestration patterns
- `azure-storage-queue` - Queue management for activities

**File**: `packages/functions/CrawlerOrchestrator/__init__.py:1`

### 3. CrawlerWorker (Queue Trigger)

**Purpose**: Performs actual web page crawling using Playwright browser automation.

**Trigger**: Queue message on `crawling-tasks-queue`

**Flow**:
1. Receives URL from queue
2. Launches headless browser (Playwright)
3. Navigates to URL, waits for JavaScript
4. Extracts article content (BeautifulSoup4)
5. Parses structured data (lxml)
6. Stores in Cosmos DB via Backend API
7. Acknowledges queue message

**Technologies**:
- **Playwright** - Headless Chrome/Firefox automation
- **BeautifulSoup4** - HTML parsing
- **lxml** - XML/HTML processing
- **LangChain** - Optional AI-powered content extraction

**Queue Configuration**:
- Queue name: `crawling-tasks-queue`
- Connection: `UP2D8_STORAGE_CONNECTION_STRING`
- Message format: JSON with `{ "url": "...", "metadata": {...} }`

**File**: `packages/functions/CrawlerWorker/__init__.py:1`

### 4. DataArchival (Timer Trigger)

**Purpose**: Archives old articles and user data to reduce active dataset size and improve query performance.

**Schedule**: Timer trigger (likely weekly/monthly)

**Flow**:
1. Identifies articles older than retention period
2. Moves to archive collection or blob storage
3. Updates indexes
4. Logs archival metrics

**Configuration**:
- Retention policies (likely in environment variables)
- Archive destination (Cosmos DB collection or Blob Storage)

**File**: `packages/functions/DataArchival/__init__.py:1`

### 5. HealthMonitor (Timer Trigger)

**Purpose**: Monitors system health, checks service availability, and alerts on failures.

**Schedule**: Timer trigger (likely every 5-15 minutes)

**Checks**:
- Cosmos DB connectivity
- Backend API health endpoint
- Queue message backlog
- Failed function executions
- Resource utilization

**Alerting**:
- Sends alerts via email/SMS when issues detected
- Logs metrics to Application Insights

**File**: `packages/functions/HealthMonitor/__init__.py:1`

### 6. ManualTrigger (HTTP Trigger)

**Purpose**: Provides HTTP endpoint for manual triggering of background tasks (testing, admin operations).

**Trigger**: HTTP GET/POST to `/api/ManualTrigger`

**Use cases**:
- Testing newsletter generation without waiting for timer
- Forcing immediate RSS feed refresh
- Triggering crawl for specific URL
- Admin operations

**Security**: Should require authentication in production (API key or Azure AD)

**File**: `packages/functions/ManualTrigger/__init__.py:1`

## Shared Services

### email_service.py

**SMTPProvider class**:
- Handles email sending via Brevo SMTP
- Supports HTML and plain text emails
- Connection pooling for efficiency
- Error handling and retry logic

**Usage**:
```python
from shared.email_service import EmailMessage, SMTPProvider

smtp = SMTPProvider(
    smtp_host="smtp-relay.brevo.com",
    smtp_port=587,
    smtp_username=os.environ["BREVO_SMTP_USER"],
    smtp_password=secret_client.get_secret("UP2D8-SMTP-KEY").value
)

message = EmailMessage(
    to_email="user@example.com",
    subject="Your Daily Newsletter",
    html_body="<h1>Headlines</h1>...",
    text_body="Headlines..."
)

smtp.send(message)
```

### backend_client.py

**Purpose**: REST client for calling Backend API from functions.

**Why needed**: Functions often need to create/update data via API instead of direct DB access to maintain data consistency and business logic.

**Usage**:
```python
from shared.backend_client import BackendClient

client = BackendClient(base_url="https://up2d8.azurewebsites.net")
client.create_article({"title": "...", "content": "..."})
```

### key_vault_client.py

**Purpose**: Centralized secret retrieval from Azure Key Vault.

**Usage**:
```python
from shared.key_vault_client import get_secret_client

secret_client = get_secret_client()
db_connection = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value
```

**Benefit**: All secrets stored securely in Key Vault, not in code or config files.

### logger_config.py

**Purpose**: Configures structured logging with `structlog` for consistent log format across all functions.

**Features**:
- JSON structured logs (easy to query in Application Insights)
- Request correlation IDs
- Automatic timestamp, function name, log level

**Usage**:
```python
from shared.logger_config import configure_logger
import structlog

configure_logger()
logger = structlog.get_logger()

logger.info("Processing article", article_id=123, user_id=456)
# Output: {"event": "Processing article", "article_id": 123, "user_id": 456, "timestamp": "...", ...}
```

### orchestration_logic.py

**Purpose**: Durable Functions orchestration patterns and activity functions.

**Contains**:
- Orchestrator functions (coordinator logic)
- Activity functions (individual work units)
- Fan-out/fan-in patterns
- Error handling and retry policies

## Important Decisions

### Decision 1: Separate Functions from Backend API
**Why**:
- Background tasks shouldn't block API requests
- Functions can scale independently
- Easier to manage long-running operations (newsletters, crawls)
- Timer triggers naturally fit serverless model

**Trade-off**: Added complexity (two deployments, shared code via `shared/`)

### Decision 2: Queue Trigger for Crawling (vs HTTP)
**Why**:
- Automatic retry on failure
- Rate limiting (control crawl speed to avoid IP bans)
- Buffering (can enqueue thousands of URLs, process at sustainable rate)
- Visibility timeout prevents duplicate processing

**Alternative**: HTTP trigger with manual queuing
**Rejected**: Reinvents Azure Queues, more error-prone

### Decision 3: Durable Functions for Orchestration
**Why**:
- Built-in checkpointing (survive restarts)
- Fan-out/fan-in for parallel crawling
- Human interaction patterns (approval workflows)
- Timer/scheduling within orchestrations

**Alternative**: Manual state management with Cosmos DB
**Rejected**: Complex, error-prone, slow

### Decision 4: Google Gemini for Newsletter Generation
**Why**:
- Free tier sufficient for POC
- Good summarization quality
- Simple API

**Alternative**: Azure OpenAI
**Considered**: Would use if scaling or need enterprise features

### Decision 5: Brevo (Sendinblue) for Email
**Why**:
- Free tier: 300 emails/day
- Reliable SMTP
- No SendGrid verification delays

**Alternative**: SendGrid
**Rejected**: SendGrid verification slow, Brevo faster to set up

## Configuration

### Environment Variables

**Shared across all functions** (`local.settings.json` or Azure Portal):

| Variable | Source | Purpose |
|----------|--------|---------|
| `FUNCTIONS_WORKER_RUNTIME` | Config | `python` |
| `AzureWebJobsStorage` | Config | Internal function storage (timers, queues, durable state) |
| `UP2D8_STORAGE_CONNECTION_STRING` | Config | Queue storage for CrawlerWorker |
| `COSMOS-DB-CONNECTION-STRING-UP2D8` | Key Vault | Cosmos DB access |
| `UP2D8-GEMINI-API-Key` | Key Vault | Google Gemini API key |
| `UP2D8-SMTP-KEY` | Key Vault | Brevo SMTP password |
| `BREVO_SMTP_HOST` | .env | `smtp-relay.brevo.com` |
| `BREVO_SMTP_PORT` | .env | `587` |
| `BREVO_SMTP_USER` | .env | `9a9964001@smtp-brevo.com` |
| `SENDER_EMAIL` | .env | `davidjmorgan26@gmail.com` |

### Function-Specific Configuration

Each function has `function.json` defining:
- Trigger type (timer, queue, http)
- Bindings (input/output)
- Schedule (for timer triggers)

**Example** - NewsletterGenerator timer:
```json
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "name": "timer",
      "type": "timerTrigger",
      "direction": "in",
      "schedule": "0 0 8 * * *"  // Daily at 8 AM UTC
    }
  ]
}
```

## Testing

### Local Testing

**Prerequisites**:
1. Azurite running (`azurite`)
2. Virtual environment activated (`source .venv/bin/activate`)
3. `local.settings.json` configured
4. Dependencies installed (`pip install -r requirements.txt`)

**Run all functions**:
```bash
npm run functions:dev
# or
cd packages/functions && func start
```

**Manual triggers**:
```bash
# Trigger NewsletterGenerator
curl -X POST http://localhost:7071/admin/functions/NewsletterGenerator

# Call ManualTrigger
curl http://localhost:7071/api/ManualTrigger?operation=test

# Add message to crawler queue
python -c "
from azure.storage.queue import QueueClient
q = QueueClient.from_connection_string('UseDevelopmentStorage=true', 'crawling-tasks-queue')
q.send_message('{\"url\": \"https://example.com\"}')
"
```

### Unit Tests

**Location**: `packages/functions/tests/`

**Run tests**:
```bash
cd packages/functions
source .venv/bin/activate
pytest
```

**Test files**:
- `test_mongo.py` - Cosmos DB integration tests
- `test_smtp.py` - Email service tests
- `migration.py` - Data migration utilities

## Common Issues

### Issue: Timer triggers not firing locally
**Cause**: `AzureWebJobsStorage` not configured or Azurite not running
**Fix**:
1. Start Azurite: `azurite`
2. Check `local.settings.json` has `"AzureWebJobsStorage": "UseDevelopmentStorage=true"`

### Issue: Queue trigger not processing messages
**Cause**: Queue doesn't exist in Azurite or function binding misconfigured
**Fix**:
1. Create queue manually: `az storage queue create --name crawling-tasks-queue --connection-string "UseDevelopmentStorage=true"`
2. Or use Azure Storage Explorer GUI to create queue

### Issue: Secrets not loading (KeyVault errors)
**Cause**: Running locally without Azure credentials
**Fix**:
1. Use `.env` file for local development instead of Key Vault
2. Or run `az login` to authenticate with Azure

### Issue: Playwright browser crashes
**Cause**: Playwright browsers not installed
**Fix**: `playwright install chromium`

## Performance Considerations

**Function timeout**: Default 5 minutes, configurable up to 10 minutes (Consumption plan)

**Scaling**:
- Timer triggers: 1 instance (singleton)
- Queue triggers: Auto-scale based on queue depth (up to 200 instances)
- HTTP triggers: Scale based on request rate

**Cold starts**:
- Python cold start: 3-10 seconds
- Mitigation: Keep functions warm with periodic pings or use Premium plan

**Cost optimization**:
- Use timer triggers for scheduled tasks (cheaper than Logic Apps)
- Batch operations where possible
- Use queue triggers for bursty workloads

## Deployment

**Azure Portal**:
- Function App: `up2d8-function-app`
- App Service Plan: `ASP-personalrg-bca8` (Consumption Y1)
- Resource Group: `personal-rg`

**CI/CD**:
- GitHub Actions from `https://github.com/djmorgan26/UP2D8-Function.git`
- Auto-deploy on push to `main` branch

**Configuration**:
- Application Settings sync with Key Vault
- Managed Identity enabled for Key Vault access

## Related Knowledge

- [Azure Functions Local Development](../patterns/azure-functions-local-dev.md) - Setup guide
- [Backend API Architecture](./backend-api-architecture.md) - Related REST API (if exists)
- [Entra ID Authentication](../features/entra-id-authentication.md) - Auth system

## Future Ideas

- [ ] Add Application Insights integration for better monitoring
- [ ] Implement dead letter queues for failed crawls
- [ ] Add retry policies to timer triggers
- [ ] Create admin dashboard for function status
- [ ] Add unit tests for each function
- [ ] Implement circuit breaker for external APIs
- [ ] Add rate limiting for crawling to avoid IP bans
- [ ] Create deployment slots for blue-green deployments
- [ ] Document durable function orchestration patterns
- [ ] Add health check aggregation dashboard

## References

- [Azure Functions Python Reference](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Durable Functions Python](https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview)
- [Azure Queue Storage Triggers](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-queue-trigger)
