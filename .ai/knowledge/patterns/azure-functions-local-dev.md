---
type: pattern
name: Azure Functions Local Development Setup
status: implemented
created: 2025-11-08
updated: 2025-11-08
files:
  - packages/functions/.venv/
  - packages/functions/.python_version
  - packages/functions/local.settings.json
  - packages/functions/requirements.txt
related:
  - ../components/azure-functions-architecture.md
tags: [azure-functions, python, local-development, azurite, virtual-environment]
---

# Azure Functions Local Development Setup

## What It Does

Configures the local development environment for Azure Functions with Python 3.11, enabling developers to run and test serverless functions locally before deployment. This pattern solves the Python version compatibility issue (Azure Functions only supports up to Python 3.11, not 3.13/3.14) and configures Azurite for local storage emulation.

## The Problem It Solves

**Python Version Mismatch**: Azure Functions Runtime (v4) only supports Python 3.9, 3.10, and 3.11. When system Python is 3.13+ (Homebrew default), the Functions runtime fails with:
```
Version 3.14 is not supported for language python
Did not find functions with language [python]
```

**Storage Dependencies**: Timer triggers, queue triggers, and durable functions require Azure Storage (blob, queue, table). Running locally requires either:
- Connection to real Azure Storage (slow, costs money, requires internet)
- Local storage emulator (Azurite - fast, free, offline)

## How It Works

### 1. Python 3.11 Virtual Environment

**Installation**:
```bash
brew install python@3.11
```

**Virtual Environment Creation**:
```bash
cd packages/functions
/opt/homebrew/bin/python3.11 -m venv .venv
```

**Activation**:
```bash
source .venv/bin/activate
python --version  # Should show 3.11.14
```

**Why this works**:
- Azure Functions Core Tools searches for `python3` in PATH
- Virtual environment puts Python 3.11's `python3` first in PATH
- Runtime successfully loads Python 3.11 worker

**Key files**:
- `.venv/bin/python3` → `/opt/homebrew/opt/python@3.11/bin/python3.11`
- `.venv/bin/activate` - Shell script that modifies PATH
- `.python_version` - Documents required Python version (3.11)

### 2. Azurite Local Storage Emulator

**Installation**:
```bash
npm install -g azurite
```

**Running Azurite**:
```bash
# In separate terminal, leave running
azurite
```

Or with custom location:
```bash
azurite --silent --location /tmp/azurite --debug /tmp/azurite/debug.log
```

**What Azurite provides**:
- Blob storage emulation (port 10000)
- Queue storage emulation (port 10001)
- Table storage emulation (port 10002)

### 3. Local Settings Configuration

**File**: `packages/functions/local.settings.json:1`

```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "UP2D8_STORAGE_CONNECTION_STRING": "UseDevelopmentStorage=true"
  },
  "ConnectionStrings": {}
}
```

**Key settings explained**:
- `FUNCTIONS_WORKER_RUNTIME: "python"` - Tells runtime to use Python worker
- `AzureWebJobsStorage: "UseDevelopmentStorage=true"` - Points to Azurite for internal function storage (required for all triggers except HTTP)
- `UP2D8_STORAGE_CONNECTION_STRING: "UseDevelopmentStorage=true"` - Points queue triggers to Azurite

**UseDevelopmentStorage=true**:
- Magic string recognized by Azure SDKs
- Expands to: `DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=...;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;`

### 4. Dependency Installation

**File**: `packages/functions/requirements.txt:1`

Dependencies must be installed in the virtual environment:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

**Key dependencies**:
- `azure-functions` - Azure Functions Python bindings
- `pymongo` - Cosmos DB MongoDB API client
- `google-generativeai` - Gemini API for AI features
- `langchain*` - LangChain for web crawling orchestration
- `playwright` - Browser automation for web scraping
- `azure-storage-queue` - Queue storage client
- `azure-identity` + `azure-keyvault-secrets` - Secret management

**Dependency resolution challenges**:
- LangChain packages have complex version constraints
- Installation can take 5-10 minutes due to backtracking
- Pre-pinning versions in requirements.txt speeds this up

## Running Functions Locally

### Complete Workflow

**Terminal 1 - Start Azurite**:
```bash
azurite
```

**Terminal 2 - Start Functions**:
```bash
cd packages/functions
source .venv/bin/activate
func start
```

**Or using npm script**:
```bash
npm run functions:dev
```

**Expected output**:
```
Azure Functions Core Tools
Core Tools Version:       4.4.0
Function Runtime Version: 4.1043.200.25453

Found Python version 3.11.14 (python3)

Functions:
  CrawlerOrchestrator: [POST,GET] http://localhost:7071/api/CrawlerOrchestrator
  CrawlerWorker: queueTrigger
  DataArchival: timerTrigger
  HealthMonitor: timerTrigger
  ManualTrigger: [GET,POST] http://localhost:7071/api/ManualTrigger
  NewsletterGenerator: timerTrigger
```

## Important Decisions

### Decision 1: Virtual Environment Over System Python
**Why**: Allows Python 3.11 coexistence with system Python 3.13/3.14 without conflicts. Developers can use latest Python for other projects while Functions uses 3.11.

**Alternative considered**: Changing system default Python to 3.11
**Rejected because**: Would break other projects expecting Python 3.13+, pyenv adds complexity

### Decision 2: Azurite Over Azure Storage
**Why**: Local development doesn't need cloud storage. Azurite is faster, free, works offline, and matches Azure Storage API exactly.

**Alternative considered**: Using real Azure Storage Account
**Rejected because**: Costs money, requires internet, slower, risks accidentally using production data

### Decision 3: UseDevelopmentStorage=true Over Manual Connection String
**Why**: Standard convention recognized by all Azure SDKs. Less error-prone than manually constructing local endpoints.

**Alternative considered**: Explicit connection string `AccountName=devstoreaccount1;...`
**Rejected because**: More verbose, easy to get wrong, `UseDevelopmentStorage=true` is the idiom

## Usage Example

### Starting a New Session

```bash
# Terminal 1: Start Azurite (leave running)
azurite

# Terminal 2: Activate venv and run functions
cd packages/functions
source .venv/bin/activate
npm run functions:dev
```

### Testing a Timer Trigger Function

```bash
# Manually invoke NewsletterGenerator (normally runs on schedule)
curl -X POST http://localhost:7071/admin/functions/NewsletterGenerator
```

### Testing a Queue Trigger Function

```python
# Add message to queue
from azure.storage.queue import QueueClient

queue = QueueClient.from_connection_string(
    "UseDevelopmentStorage=true",
    "crawling-tasks-queue"
)
queue.send_message("https://example.com")
```

CrawlerWorker will automatically process the message.

## Testing

**Manual testing**:
- Start Azurite in Terminal 1
- Start Functions in Terminal 2
- Use curl/Postman to invoke HTTP triggers
- Use Azure Storage Explorer to inspect queues/blobs in Azurite

**Automated tests**:
- `packages/functions/tests/` - Unit tests for functions
- Run with: `cd packages/functions && source .venv/bin/activate && pytest`

## Common Issues

### Issue 1: "Version 3.14 is not supported"
**Symptom**: Functions fail to start with Python version error
**Cause**: Not using virtual environment, system Python is 3.13/3.14
**Fix**: Activate `.venv` before running: `source .venv/bin/activate`

### Issue 2: "Missing value for AzureWebJobsStorage"
**Symptom**: Functions fail to load with storage connection error
**Cause**: Azurite not running or `local.settings.json` missing storage config
**Fix**:
1. Start Azurite in separate terminal
2. Ensure `local.settings.json` has `"AzureWebJobsStorage": "UseDevelopmentStorage=true"`

### Issue 3: "Port 7071 is unavailable"
**Symptom**: Functions fail to start, port already in use
**Cause**: Previous Functions process still running
**Fix**:
```bash
lsof -ti:7071 | xargs kill -9
# Or specify different port
func start --port 7072
```

### Issue 4: Slow dependency installation
**Symptom**: `pip install -r requirements.txt` takes 10+ minutes
**Cause**: LangChain packages have complex version dependencies causing pip backtracking
**Fix**: Pin specific versions in `requirements.txt` or wait patiently

### Issue 5: "Cannot find value named 'UP2D8_STORAGE_CONNECTION_STRING'"
**Symptom**: Warning at startup about missing connection string
**Cause**: Queue-triggered functions need explicit storage connection config
**Fix**: Already resolved in `local.settings.json:6` - `"UP2D8_STORAGE_CONNECTION_STRING": "UseDevelopmentStorage=true"`

## Environment Variables

**Local development** (`local.settings.json`):
- Auto-loaded by Azure Functions runtime
- NOT committed to git (contains secrets in production)
- Uses Azurite connection strings

**Production** (Azure Portal):
- Configured in Azure Functions App Configuration
- Uses real Azure Storage connection strings
- Pulls secrets from Azure Key Vault

**Environment-specific values**:
| Variable | Local Value | Production Value |
|----------|-------------|------------------|
| `AzureWebJobsStorage` | `UseDevelopmentStorage=true` | `@Microsoft.KeyVault(SecretUri=...)` |
| `UP2D8_STORAGE_CONNECTION_STRING` | `UseDevelopmentStorage=true` | Real Azure Storage connection |
| `COSMOS-DB-CONNECTION-STRING-UP2D8` | (from `.env` or Key Vault) | `@Microsoft.KeyVault(...)` |

## Related Knowledge

- [Azure Functions Architecture](../components/azure-functions-architecture.md) - Overview of all functions
- [Backend API Local Dev](./backend-api-local-dev.md) - Related FastAPI setup (if exists)

## Future Ideas

- [ ] Add Docker Compose file to start Azurite + Functions together
- [ ] Create VS Code launch configuration for debugging Functions
- [ ] Add pre-commit hook to validate Python 3.11 in venv
- [ ] Document hot-reload behavior and limitations
- [ ] Add script to seed Azurite with test data
- [ ] Create .env.local template for developers
- [ ] Add health check endpoint to verify all dependencies loaded

## References

- [Azure Functions Python Developer Guide](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Azurite Documentation](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azurite)
- [Azure Functions Core Tools](https://github.com/Azure/azure-functions-core-tools)
