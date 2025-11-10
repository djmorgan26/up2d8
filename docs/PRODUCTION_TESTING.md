# Production Testing Guide

Comprehensive guide for testing UP2D8 services in production on Azure.

## Overview

This testing suite provides automated integration tests and health monitoring for all UP2D8 production services:

- **Backend API** (Azure App Service)
- **Azure Functions** (Serverless functions)
- **Frontend** (Azure Static Web Apps)
- **Database** (Cosmos DB with MongoDB API)

## Test Suite Structure

```
tests/production/
├── conftest.py              # Test configuration and fixtures
├── test_backend_api.py      # Backend API tests
├── test_azure_functions.py  # Azure Functions tests
├── test_frontend.py         # Frontend tests
├── test_database.py         # Database tests
└── test_integration.py      # End-to-end integration tests
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-test.txt
```

### 2. Run Tests in Mock Mode (Safe)

```bash
export PROD_TEST_MODE=mock
pytest tests/production/ -v
```

All tests will be skipped when in mock mode - this is safe for CI/CD.

### 3. Run Tests Against Production

```bash
export PROD_TEST_MODE=live
pytest tests/production/ -v
```

**⚠️ WARNING:** This makes real requests to production services.

### 4. Run Only Critical Tests

```bash
export PROD_TEST_MODE=live
pytest tests/production/ -v -m critical
```

## Test Modes

### Mock Mode (Default)

```bash
export PROD_TEST_MODE=mock
pytest tests/production/
```

- **Safe for CI/CD**: No real requests to production
- **Tests are skipped**: All production tests are marked as skipped
- **Use for**: Development, pull request checks

### Live Mode

```bash
export PROD_TEST_MODE=live
pytest tests/production/
```

- **Tests production**: Makes real HTTP requests to Azure services
- **Use for**: Post-deployment verification, scheduled monitoring
- **Requires**: Azure credentials and network access

## Test Markers

Tests are organized with pytest markers:

### `@pytest.mark.production`
All production tests have this marker. Automatically skipped unless `PROD_TEST_MODE=live`.

### `@pytest.mark.critical`
Critical tests that must pass for service health:
- Service availability
- SSL certificate validity
- Database connectivity
- Core endpoint functionality

```bash
# Run only critical tests
pytest tests/production/ -m critical
```

### `@pytest.mark.slow`
Slow tests (>5 seconds):
- Response time tests
- Performance benchmarks

```bash
# Skip slow tests
pytest tests/production/ -m "not slow"
```

## Configuration

### Environment Variables

Create `tests/production/.env` (see `.env.example`):

```bash
# Test mode
PROD_TEST_MODE=mock

# Service URLs
AZURE-BACKEND-APP-URL=https://up2d8.azurewebsites.net
AZURE-FUNCTION-APP-URL=https://up2d8-function-app.azurewebsites.net/
AZURE-FRONTEND-APP-URL=https://gray-wave-00bdfc60f.3.azurestaticapps.net

# Test configuration
PROD_TEST_TIMEOUT=30
```

### Test Runner Script

Use the provided script for easier testing:

```bash
# Run in mock mode
./scripts/run_production_tests.sh --mock

# Run against production
./scripts/run_production_tests.sh --live

# Run only critical tests
./scripts/run_production_tests.sh --live --critical-only
```

## Test Coverage

### Backend API Tests (`test_backend_api.py`)

**Critical Tests:**
- ✅ API health check (`/`)
- ✅ OpenAPI schema availability
- ✅ SSL certificate validation

**Endpoint Tests:**
- Articles endpoint (`/articles`)
- RSS feeds endpoint (`/rss-feeds`)
- Users endpoint (`/users`)
- Chat endpoint (`/chat`)
- Analytics endpoint (`/analytics`)
- Feedback endpoint (`/feedback`)

**Performance Tests:**
- Response time < 5 seconds
- CORS headers configured

### Azure Functions Tests (`test_azure_functions.py`)

**Critical Tests:**
- ✅ Function app health
- ✅ SSL certificate validation
- RSS scraper function
- Newsletter generator function
- Web crawler orchestrator

**Configuration Tests:**
- Admin endpoint protection
- CORS configuration
- Response time < 10 seconds

### Frontend Tests (`test_frontend.py`)

**Critical Tests:**
- ✅ Static site availability
- ✅ SSL certificate validation

**Content Tests:**
- HTML content returned
- React root element present

**Performance Tests:**
- Response time < 5 seconds
- Security headers present
- Caching headers configured
- 404 handling

### Database Tests (`test_database.py`)

**Critical Tests:**
- Database connection
- Required collections exist
- Write permissions

**Schema Tests:**
- Users collection schema
- Articles collection schema
- RSS feeds collection schema

**Performance Tests:**
- Query performance < 2 seconds
- Connection pooling
- Index validation

### Integration Tests (`test_integration.py`)

**Critical Tests:**
- ✅ Full stack health (all services)
- ✅ SSL certificates across services

**Flow Tests:**
- Backend to database flow
- Service response times
- CORS configuration
- Error handling consistency

## Health Monitoring

### Health Check Script

Continuously monitor production services:

```bash
python scripts/health_check.py
```

**Output:**
```
======================================================================
UP2D8 Production Health Check - 2025-11-10 10:08:59
======================================================================

✅ Backend API
   URL: https://up2d8.azurewebsites.net
   Status: HEALTHY
   HTTP Status: 200
   Response Time: 0.412s

✅ Function App
   URL: https://up2d8-function-app.azurewebsites.net/
   Status: HEALTHY
   HTTP Status: 200
   Response Time: 0.670s

✅ Frontend
   URL: https://gray-wave-00bdfc60f.3.azurestaticapps.net
   Status: HEALTHY
   HTTP Status: 200
   Response Time: 0.631s

======================================================================
Summary: All 3 services are operational
======================================================================
```

### Save Health Check Results

```bash
python scripts/health_check.py --save
```

Results saved to `health-checks/health_check_TIMESTAMP.json`.

### Exit Codes

- `0`: All services healthy
- `1`: One or more services have critical issues

Use in monitoring scripts:
```bash
if ! python scripts/health_check.py; then
    echo "Health check failed! Alerting..."
    # Send alert (Slack, email, PagerDuty, etc.)
fi
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Production Tests

on:
  schedule:
    - cron: '0 */4 * * *'  # Every 4 hours
  workflow_dispatch:       # Manual trigger

jobs:
  production-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements-test.txt

      - name: Run critical production tests
        env:
          PROD_TEST_MODE: live
          AZURE-BACKEND-APP-URL: ${{ secrets.AZURE_BACKEND_APP_URL }}
          AZURE-FUNCTION-APP-URL: ${{ secrets.AZURE_FUNCTION_APP_URL }}
          AZURE-FRONTEND-APP-URL: ${{ secrets.AZURE_FRONTEND_APP_URL }}
        run: pytest tests/production/ -m critical -v

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: test-reports/
```

### Azure DevOps

```yaml
trigger: none

schedules:
- cron: "0 */4 * * *"
  displayName: Every 4 hours
  branches:
    include:
    - main

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.11'

- script: pip install -r requirements-test.txt
  displayName: 'Install dependencies'

- script: |
    export PROD_TEST_MODE=live
    pytest tests/production/ -m critical -v --html=test-reports/report.html
  displayName: 'Run production tests'

- task: PublishTestResults@2
  condition: always()
  inputs:
    testResultsFiles: 'test-reports/*.xml'
```

### Scheduled Monitoring

Set up a cron job for continuous monitoring:

```bash
# Add to crontab (crontab -e)
# Run health check every 15 minutes
*/15 * * * * cd /path/to/up2d8 && ./scripts/health_check.py --save >> logs/health_check.log 2>&1

# Run full test suite every 4 hours
0 */4 * * * cd /path/to/up2d8 && ./scripts/run_production_tests.sh --live --critical-only >> logs/production_tests.log 2>&1
```

## Test Results Analysis

### Current Production Status

Based on the latest test run:

**✅ Passing (25 tests):**
- All critical health checks
- SSL certificates valid across all services
- Frontend fully operational
- Response times within acceptable limits

**⚠️ Issues Found (11 tests):**
- Backend API endpoints returning 404 (may not be deployed yet)
- Azure Functions endpoints returning 404 (may not be deployed yet)
- Database tests skipped (KeyVault import issue)

### Interpreting Results

**404 Errors on Endpoints:**
- Endpoints may not exist yet
- Routes may be different than expected
- Authentication may be blocking access
- **Action:** Review OpenAPI schema at `/docs` to verify endpoints

**Database Test Skips:**
- Import path issues with shared modules
- **Action:** Fix import paths or run database tests separately

**SSL Certificate Tests:**
- All passing - certificates are valid and properly configured

## Troubleshooting

### Tests Won't Run

**Problem:** Tests are all skipped
```bash
# Solution: Set test mode to live
export PROD_TEST_MODE=live
```

### Connection Timeout

**Problem:** Tests timeout connecting to services
```bash
# Solution: Increase timeout
export PROD_TEST_TIMEOUT=60
```

### 404 Errors

**Problem:** Endpoints return 404
1. Check service is deployed: `curl https://up2d8.azurewebsites.net/`
2. Check OpenAPI docs: `https://up2d8.azurewebsites.net/docs`
3. Verify endpoint paths match expectations

### Database Tests Fail

**Problem:** Cannot connect to database
1. Check Azure credentials: `az account show`
2. Verify Key Vault access
3. Check connection string is correct

## Best Practices

1. **Run mock tests in CI/CD** - Don't burden production with every PR
2. **Schedule live tests** - Run critical tests every 4 hours
3. **Monitor health continuously** - Run health check every 15 minutes
4. **Alert on failures** - Integrate with monitoring tools
5. **Review test results weekly** - Keep tests updated with production changes
6. **Test after deployments** - Always verify deployment success

## Next Steps

1. **Fix endpoint 404s** - Verify backend API routes match test expectations
2. **Fix database tests** - Resolve import path issues
3. **Add authentication** - Tests currently don't authenticate
4. **Add more assertions** - Verify response data structure
5. **Performance baselines** - Track response time trends over time
6. **Alert integration** - Connect to Slack/PagerDuty/etc.

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Azure App Service Monitoring](https://docs.microsoft.com/azure/app-service/monitor)
- [Azure Functions Monitoring](https://docs.microsoft.com/azure/azure-functions/functions-monitoring)
- [Application Insights](https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview)
