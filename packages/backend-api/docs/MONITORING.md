# UP2D8 Backend API - Monitoring & Observability

This document describes the monitoring and observability setup for the UP2D8 Backend API.

## Overview

The monitoring setup uses **FREE, built-in Python capabilities** with no additional cost:

- **Structured JSON logging** for easy parsing and analysis
- **Request/response logging middleware** for automatic request tracking
- **Enhanced health check endpoint** for service monitoring
- **Optional Application Insights integration** (free tier available, not enabled by default)

## Structured Logging

### Configuration

Logging is configured automatically on application startup via `logging_config.py`.

**Default settings:**
- Log level: `INFO` (configurable via `LOG_LEVEL` environment variable)
- Format: Structured JSON (configurable via `STRUCTURED_LOGGING` environment variable)
- Output: stdout (captured by container/Azure App Service logs)

**Environment variables:**
```bash
# Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Enable/disable structured logging (true/false)
STRUCTURED_LOGGING=true
```

### Log Format

Each log entry is a JSON object with the following structure:

```json
{
  "timestamp": "2025-11-10T15:30:45.123456+00:00",
  "level": "INFO",
  "logger": "api.chat",
  "message": "Chat request processed successfully",
  "extra": {
    "user_id": "abc123",
    "request_id": "d4e5f6g7-h8i9-j0k1-l2m3-n4o5p6q7r8s9",
    "duration_ms": 342.15
  }
}
```

### Using Logging in Code

**Basic usage:**
```python
import logging

logger = logging.getLogger(__name__)

# Simple log message
logger.info("User created successfully")

# Log with additional context
logger.info(
    "Article processed",
    extra={
        "article_id": "123",
        "user_id": "abc",
        "processing_time_ms": 150
    }
)

# Error logging with exception info
try:
    process_article(article_id)
except Exception as e:
    logger.error(
        f"Failed to process article {article_id}",
        exc_info=True  # Include full traceback
    )
```

**Using logger with context:**
```python
from logging_config import get_logger_with_context

# Create logger with persistent context
logger = get_logger_with_context(
    __name__,
    service="backend-api",
    version="1.0.0"
)

# All log entries will include service and version
logger.info("Request processed")
```

## Request Logging Middleware

The `RequestLoggingMiddleware` automatically logs all incoming requests and outgoing responses.

### What It Logs

**For each request:**
- Unique request ID (UUID)
- HTTP method and path
- Query parameters
- Client IP address
- User agent
- Request duration (milliseconds)
- Response status code

**Example log entries:**

```json
{
  "timestamp": "2025-11-10T15:30:45.123456+00:00",
  "level": "INFO",
  "logger": "middleware.logging_middleware",
  "message": "Incoming request: POST /api/chat",
  "extra": {
    "request_id": "d4e5f6g7-h8i9-j0k1-l2m3-n4o5p6q7r8s9",
    "method": "POST",
    "path": "/api/chat",
    "query_params": null,
    "client_ip": "192.168.1.100",
    "user_agent": "Mozilla/5.0..."
  }
}

{
  "timestamp": "2025-11-10T15:30:45.465456+00:00",
  "level": "INFO",
  "logger": "middleware.logging_middleware",
  "message": "Request completed: POST /api/chat - 200",
  "extra": {
    "request_id": "d4e5f6g7-h8i9-j0k1-l2m3-n4o5p6q7r8s9",
    "method": "POST",
    "path": "/api/chat",
    "status_code": 200,
    "duration_ms": 342.15
  }
}
```

### Excluded Paths

To reduce log noise, the following paths are excluded from request logging:
- `/` (root endpoint)
- `/api/health` (health check - called frequently by monitoring tools)

You can modify excluded paths in `main.py`:
```python
app.add_middleware(
    RequestLoggingMiddleware,
    exclude_paths=["/", "/api/health", "/docs"]  # Add more paths as needed
)
```

### Request Tracing

The middleware adds an `X-Request-ID` header to all responses, allowing you to trace requests across logs:

```bash
curl -i http://localhost:8000/api/chat
# Response includes:
# X-Request-ID: d4e5f6g7-h8i9-j0k1-l2m3-n4o5p6q7r8s9
```

You can also access the request ID in route handlers:
```python
from fastapi import Request

@router.post("/api/chat")
async def chat(request: Request):
    request_id = request.state.request_id
    logger.info(f"Processing chat request", extra={"request_id": request_id})
```

## Health Check Endpoint

### Endpoint Details

**URL:** `GET /api/health`
**Authentication:** None (public endpoint)

### Response Format

**Healthy response (200 OK):**
```json
{
  "status": "healthy",
  "service": "UP2D8 Backend API",
  "version": "1.0.0",
  "timestamp": "2025-11-10T15:30:45.123456+00:00",
  "database": {
    "status": "connected",
    "ping_ok": true
  },
  "collections": {
    "articles": {
      "total": 1523,
      "unprocessed": 47,
      "processed": 1476
    },
    "users": 89,
    "rss_feeds": 25
  }
}
```

**Unhealthy response (200 OK with error):**
```json
{
  "status": "unhealthy",
  "service": "UP2D8 Backend API",
  "version": "1.0.0",
  "error": "Database connection timeout",
  "timestamp": "2025-11-10T15:30:45.123456+00:00"
}
```

### Using for Monitoring

**1. Load Balancer Health Checks:**

Most load balancers can check `/api/health` and route traffic only to healthy instances.

**Azure App Service health check configuration:**
```bash
# In Azure Portal > App Service > Health check
Path: /api/health
```

**2. Uptime Monitoring:**

Use free uptime monitoring services to check the health endpoint:
- Azure Monitor (free tier: 10 tests)
- UptimeRobot (free tier: 50 monitors)
- Pingdom (free tier: 1 monitor)

**3. Custom Monitoring Scripts:**

```bash
#!/bin/bash
# Simple health check script

RESPONSE=$(curl -s http://your-api.azurewebsites.net/api/health)
STATUS=$(echo $RESPONSE | jq -r '.status')

if [ "$STATUS" != "healthy" ]; then
  echo "API is unhealthy!"
  echo $RESPONSE | jq
  exit 1
fi

echo "API is healthy"
```

## Viewing Logs

### Local Development

When running locally, logs are printed to stdout in JSON format:

```bash
# Run the API
cd packages/backend-api
uvicorn main:app --reload

# Logs will appear in console as JSON
```

### Azure App Service

Logs are automatically captured by Azure App Service and available in:

**1. Azure Portal:**
- App Service > Monitoring > Log stream (real-time)
- App Service > Monitoring > App Service logs (historical)

**2. Azure CLI:**
```bash
# Stream logs in real-time
az webapp log tail --name your-app-name --resource-group your-rg

# Download logs
az webapp log download --name your-app-name --resource-group your-rg
```

**3. Azure Storage (if configured):**
- Logs can be archived to Azure Blob Storage for long-term retention
- Configuration: App Service > App Service logs > Application Logging (Blob)

### Analyzing Logs

**Using `jq` to parse JSON logs:**

```bash
# Filter logs by level
cat app.log | grep ERROR

# Extract specific fields
cat app.log | jq -r 'select(.level == "ERROR") | "\(.timestamp) - \(.message)"'

# Find slow requests (duration > 1000ms)
cat app.log | jq -r 'select(.extra.duration_ms > 1000) | "\(.extra.request_id) - \(.extra.duration_ms)ms"'

# Count requests by path
cat app.log | jq -r 'select(.message | startswith("Request completed")) | .extra.path' | sort | uniq -c
```

## Optional: Application Insights Integration

**Note:** Application Insights has a **free tier** (5 GB/month ingestion), but this is NOT enabled by default to avoid any costs. Enable only if needed.

### Free Tier Limits
- 5 GB data ingestion per month (free)
- 90-day retention (free)
- Basic alerting (free)

### Setup (Optional)

**1. Create Application Insights resource:**
```bash
az monitor app-insights component create \
  --app your-app-insights-name \
  --location eastus \
  --resource-group your-rg \
  --application-type web
```

**2. Get instrumentation key:**
```bash
az monitor app-insights component show \
  --app your-app-insights-name \
  --resource-group your-rg \
  --query instrumentationKey -o tsv
```

**3. Install OpenTelemetry SDK:**
```bash
pip install opentelemetry-api opentelemetry-sdk
pip install azure-monitor-opentelemetry
```

**4. Configure in `main.py`:**
```python
import os
from azure.monitor.opentelemetry import configure_azure_monitor

# Only configure if instrumentation key is set
if instrumentation_key := os.getenv("APPLICATIONINSIGHTS_INSTRUMENTATION_KEY"):
    configure_azure_monitor(
        connection_string=f"InstrumentationKey={instrumentation_key}"
    )
```

**5. Set environment variable:**
```bash
export APPLICATIONINSIGHTS_INSTRUMENTATION_KEY="your-key-here"
```

### Benefits of Application Insights

Once enabled (optional):
- Automatic request tracking with dependency maps
- Performance monitoring and anomaly detection
- Custom metrics and dashboards
- Alerts based on metrics or log patterns
- Live metrics stream

## Alerting (Free Options)

### 1. Azure Monitor Alerts (Free Tier)

**Free tier includes:**
- 10 metric alert rules
- Email/SMS notifications

**Example: Alert on high error rate:**
```bash
# Create alert when HTTP 500 errors exceed 5 in 5 minutes
az monitor metrics alert create \
  --name high-error-rate \
  --resource-group your-rg \
  --scopes /subscriptions/.../resourceGroups/your-rg/providers/Microsoft.Web/sites/your-app \
  --condition "count Http5xx > 5" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action email your-email@example.com
```

### 2. Health Check Monitoring

Use free uptime monitoring services:
- **UptimeRobot** (free: 50 monitors, 5-min intervals)
- **Pingdom** (free: 1 monitor)
- **Azure Monitor** (free tier: 10 tests)

### 3. Log-based Alerts

Use Azure Log Analytics (free tier: 5 GB/month) to create alerts based on log queries.

## Best Practices

### 1. Log Levels

Use appropriate log levels:
- **DEBUG**: Detailed diagnostic info (disable in production)
- **INFO**: General informational messages (requests, business events)
- **WARNING**: Something unexpected but not critical
- **ERROR**: Error that needs attention
- **CRITICAL**: Severe error that may cause app shutdown

### 2. Structured Fields

Always use `extra` parameter for structured data:

```python
# Good
logger.info("User created", extra={"user_id": user.id, "email": user.email})

# Bad (harder to query)
logger.info(f"User created: {user.id}, {user.email}")
```

### 3. Sensitive Data

**Never log sensitive information:**
- Passwords
- API keys
- Personal identifiable information (PII) - unless necessary and compliant
- Credit card numbers

```python
# Good
logger.info("User authenticated", extra={"user_id": user.id})

# Bad
logger.info(f"User logged in with password: {password}")
```

### 4. Cost Management

To stay within free tiers:
- Use log levels appropriately (avoid DEBUG in production)
- Exclude noisy endpoints from request logging
- Set log retention policies
- Monitor ingestion volumes

**Check Application Insights usage:**
```bash
az monitor app-insights metrics show \
  --app your-app-insights-name \
  --resource-group your-rg \
  --metrics "billableIngestionVolume"
```

## Troubleshooting

### Logs Not Appearing

1. **Check log level**: Ensure `LOG_LEVEL` is set to `INFO` or lower
2. **Check stdout**: Logs go to stdout, ensure it's not redirected
3. **Azure App Service**: Enable Application Logging in Azure Portal

### High Log Volume

1. **Increase excluded paths**: Add more paths to `exclude_paths` in middleware
2. **Increase log level**: Set `LOG_LEVEL=WARNING` to reduce verbosity
3. **Sample logs**: Implement log sampling for high-traffic endpoints

### Structured Logging Not Working

1. **Check environment variable**: Ensure `STRUCTURED_LOGGING` is not set to `false`
2. **Verify configuration**: Check `logging_config.py` is being called in `main.py`
3. **Test locally**: Run locally and check console output

## Summary

The monitoring setup provides:

✅ **FREE structured JSON logging** for all application events
✅ **FREE automatic request/response tracking** with timing
✅ **FREE health check endpoint** for monitoring service status
✅ **FREE log viewing** in Azure Portal and CLI
✅ **OPTIONAL Application Insights** (free tier available, not enabled by default)

**Cost:** $0/month with current configuration

**To enable Application Insights (optional):**
- Free tier: 5 GB/month ingestion
- Follow "Optional: Application Insights Integration" section above
