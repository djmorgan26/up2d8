# Backend API Test Suite

## Overview

Comprehensive test suite for the UP2D8 Backend API using pytest and mocking.

**Total Tests**: 53 tests across 9 API endpoint groups

## Test Coverage

### API Endpoints

| Endpoint | Tests | Coverage |
|----------|-------|----------|
| `/` (Root) | 1 | Basic health check |
| `/api/health` | 3 | Health check, database status, error handling |
| `/api/articles` | 8 | CRUD operations, edge cases, error handling |
| `/api/users` | 8 | User creation, updates, migration, validation |
| `/api/rss_feeds` | 8 | CRUD operations, validation, error handling |
| `/api/chat` | 12 | Chat with AI, web search grounding, sessions, messages |
| `/api/topics/suggest` | 9 | AI topic suggestions, input validation, error handling |
| `/api/feedback` | 2 | Feedback submission, validation |
| `/api/analytics` | 2 | Analytics logging, validation |

### Test Distribution

```
test_analytics.py:   2 tests
test_articles.py:    8 tests (NEW: 5 edge case tests added)
test_chat.py:       12 tests (NEW: 6 comprehensive tests added)
test_feedback.py:    2 tests
test_health.py:      3 tests (NEW: complete coverage)
test_root.py:        1 test
test_rss_feeds.py:   8 tests
test_topics.py:      9 tests (NEW: complete coverage)
test_users.py:       8 tests
-----------------------------------
TOTAL:              53 tests
```

## Running Tests

### Install Dependencies

```bash
cd packages/backend-api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run All Tests

```bash
# From backend-api directory
pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=api --cov-report=html

# Run specific test file
pytest tests/api/test_chat.py

# Run specific test
pytest tests/api/test_chat.py::test_chat_endpoint_with_sources
```

### From Root Directory

```bash
npm run test:backend
```

## Test Structure

### Fixtures (`conftest.py`)

- **`test_client`**: Provides FastAPI TestClient with mocked database
- **`real_mongo_db`**: Real MongoDB connection for integration tests (session scope)

### Test Patterns

All tests use mocking to avoid external dependencies:

```python
def test_example(test_client, mocker):
    client, mock_db_client = test_client

    # Configure mock behavior
    mock_db_client.collection.find.return_value = [...]

    # Make request
    response = client.get("/api/endpoint")

    # Assertions
    assert response.status_code == 200
    assert response.json() == expected_data
```

## New Test Additions (2025-11-09)

### Health Endpoint Tests (3 tests)
- ✅ `test_health_check_healthy` - Successful health check with all metrics
- ✅ `test_health_check_unhealthy` - Database connection failure handling
- ✅ `test_health_check_partial_failure` - Partial metric collection failure

### Topics Endpoint Tests (9 tests)
- ✅ `test_suggest_topics_with_query` - Query-based suggestions
- ✅ `test_suggest_topics_with_interests` - Interest-based suggestions
- ✅ `test_suggest_topics_no_input` - Default popular topics
- ✅ `test_suggest_topics_with_numbered_response` - Cleanup numbered lists
- ✅ `test_suggest_topics_with_bullet_points` - Cleanup bullet points
- ✅ `test_suggest_topics_limits_to_8` - Max 8 suggestions limit
- ✅ `test_suggest_topics_gemini_error` - Gemini API error handling
- ✅ `test_suggest_topics_empty_response` - Empty response handling
- ✅ `test_suggest_topics_invalid_request` - Request validation

### Enhanced Chat Tests (6 new tests)
- ✅ `test_chat_endpoint_with_sources` - Web search grounding with sources
- ✅ `test_chat_endpoint_empty_prompt` - Empty prompt validation
- ✅ `test_chat_endpoint_long_prompt` - Very long prompt handling
- ✅ `test_chat_endpoint_gemini_api_error` - Gemini API error handling
- ✅ `test_chat_endpoint_invalid_request` - Request validation (2 scenarios)

### Enhanced Articles Tests (5 new tests)
- ✅ `test_get_articles_empty_database` - Empty results handling
- ✅ `test_get_articles_missing_fields` - Partial data handling
- ✅ `test_get_articles_with_special_characters` - Special character encoding
- ✅ `test_get_articles_database_error` - Database error handling
- ✅ `test_get_article_with_invalid_id_format` - Invalid ID formats

## Test Coverage Highlights

### Critical Paths Covered
- ✅ User authentication and migration (Entra ID user_id flow)
- ✅ AI chat with web search grounding and source extraction
- ✅ RSS feed CRUD operations
- ✅ Article retrieval and data transformation
- ✅ Topic suggestions with AI
- ✅ Session management for chat
- ✅ Health monitoring and metrics

### Edge Cases Covered
- Empty/null data handling
- Missing required fields
- Database connection errors
- API rate limit errors
- Invalid input validation
- Special characters in data
- Very long inputs
- Partial failures

### Error Handling
- 400 Bad Request (validation errors)
- 404 Not Found (missing resources)
- 422 Unprocessable Entity (invalid data)
- 500 Internal Server Error (API/DB failures)

## Areas for Future Enhancement

### Missing Coverage
1. **Integration Tests**: End-to-end tests with real database
2. **Performance Tests**: Load testing for high traffic scenarios
3. **Security Tests**: SQL injection, XSS, auth bypass attempts
4. **Rate Limiting Tests**: API rate limit enforcement

### Recommended Next Steps
1. Add pytest-cov for code coverage metrics
2. Add integration tests for critical user journeys
3. Add load tests for chat endpoint (most resource-intensive)
4. Add security audit tests for all endpoints
5. Add contract tests between backend and frontend

## Best Practices

### When Writing New Tests

1. **Name tests descriptively**: `test_<feature>_<scenario>`
2. **Use docstrings**: Explain what the test validates
3. **Mock external dependencies**: Database, APIs, etc.
4. **Test happy path AND edge cases**: Both success and failure scenarios
5. **Assert multiple aspects**: Status code, response data, mock calls
6. **Clean up**: Clear dependency overrides after each test

### Example Test Template

```python
def test_endpoint_scenario(test_client, mocker):
    """Test description explaining what is being validated"""
    client, mock_db_client = test_client

    # Setup - configure mocks
    mock_db_client.collection.method.return_value = expected_data

    # Execute - make API request
    response = client.post("/api/endpoint", json=request_data)

    # Assert - verify results
    assert response.status_code == 200
    assert response.json() == expected_response
    mock_db_client.collection.method.assert_called_once()

    # Cleanup (if needed)
    app.dependency_overrides = {}
```

## Continuous Integration

Tests should run on every:
- Pull request
- Commit to main branch
- Deployment to staging/production

Configure GitHub Actions to run:
```bash
pytest -v --cov=api --cov-report=xml
```

## Troubleshooting

### Common Issues

**Import Errors**:
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

**Mock Not Working**:
- Check the import path in `mocker.patch()`
- Ensure you're patching where the object is used, not where it's defined

**Database Tests Failing**:
- Check MongoDB connection string in environment
- Ensure test database is accessible

**Async Function Errors**:
- FastAPI test client handles async automatically
- No need for `await` in tests

## Contributing

When adding new API endpoints:
1. Create corresponding test file in `tests/api/`
2. Add at least 3 tests: happy path, validation error, database error
3. Update this README with test count
4. Ensure all tests pass before committing

---

**Last Updated**: 2025-11-09
**Test Framework**: pytest
**Total Tests**: 53
**Coverage Goal**: >70% for production code
