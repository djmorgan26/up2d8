# UP2D8 Test Suite

Comprehensive test suite for the UP2D8 backend API.

## Test Structure

```
tests/
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_llm_provider.py
│   ├── test_embeddings.py
│   ├── test_vector_db.py
│   ├── test_email_provider.py
│   ├── services/
│   │   ├── test_scraper.py
│   │   ├── test_summarizer.py
│   │   └── test_digest_generator.py
│   └── utils/
│       └── test_helpers.py
│
├── integration/             # Integration tests (with DB, Redis)
│   ├── test_api_auth.py
│   ├── test_api_articles.py
│   ├── test_api_digests.py
│   ├── test_api_chat.py
│   ├── test_scraping_pipeline.py
│   └── test_digest_pipeline.py
│
├── e2e/                    # End-to-end tests (full workflows)
│   ├── test_user_onboarding.py
│   ├── test_digest_delivery.py
│   └── test_chat_session.py
│
├── fixtures/               # Shared test data
│   ├── sample_articles.json
│   ├── sample_users.json
│   └── mock_responses.py
│
├── conftest.py            # Pytest configuration & fixtures
└── README.md              # This file
```

## Running Tests

### All Tests
```bash
pytest
```

### By Category
```bash
# Unit tests only (fast)
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# End-to-end tests
pytest tests/e2e/ -v
```

### By Marker
```bash
# Run only unit tests
pytest -m unit

# Skip slow tests
pytest -m "not slow"

# Run tests that require Ollama
pytest -m requires_ollama

# Run integration tests that need database
pytest -m "integration and requires_db"
```

### Specific Tests
```bash
# Single test file
pytest tests/unit/test_llm_provider.py -v

# Single test class
pytest tests/unit/test_llm_provider.py::TestLLMFactory -v

# Single test function
pytest tests/unit/test_llm_provider.py::TestLLMFactory::test_create_ollama_client -v

# Tests matching pattern
pytest -k "test_ollama" -v
```

### With Coverage
```bash
# Generate coverage report
pytest --cov=api --cov-report=html

# View coverage in browser
open htmlcov/index.html
```

## Test Categories

### Unit Tests (`tests/unit/`)
- **Purpose**: Test individual functions/classes in isolation
- **Speed**: Fast (< 1 second per test)
- **Dependencies**: Mocked
- **When to Run**: On every commit
- **Example**:
  ```python
  def test_llm_factory_creates_ollama_client():
      with patch.dict(os.environ, {"LLM_PROVIDER": "ollama"}):
          client = LLMFactory.create_client()
          assert isinstance(client, OllamaClient)
  ```

### Integration Tests (`tests/integration/`)
- **Purpose**: Test service interactions
- **Speed**: Medium (1-5 seconds per test)
- **Dependencies**: Real DB and Redis (Docker), mocked external APIs
- **When to Run**: Before PR merge
- **Example**:
  ```python
  @pytest.mark.integration
  def test_api_create_user(client, sample_user_data):
      response = client.post("/auth/signup", json=sample_user_data)
      assert response.status_code == 201
  ```

### End-to-End Tests (`tests/e2e/`)
- **Purpose**: Test complete user workflows
- **Speed**: Slow (5-30 seconds per test)
- **Dependencies**: All services running
- **When to Run**: Before releases
- **Example**:
  ```python
  @pytest.mark.e2e
  async def test_digest_delivery_workflow(client, db_session):
      # 1. User signs up
      # 2. Sets preferences
      # 3. Articles scraped
      # 4. Digest generated
      # 5. Email delivered
      # 6. User reads digest
      pass
  ```

## Test Markers

Organize and filter tests using markers:

- `@pytest.mark.unit` - Unit test
- `@pytest.mark.integration` - Integration test
- `@pytest.mark.e2e` - End-to-end test
- `@pytest.mark.slow` - Slow test (> 1 second)
- `@pytest.mark.requires_ollama` - Needs Ollama running
- `@pytest.mark.requires_db` - Needs database
- `@pytest.mark.requires_redis` - Needs Redis

## Fixtures

Common fixtures available in all tests (defined in `conftest.py`):

### Database Fixtures
- `test_db_engine` - Test database engine (SQLite in-memory)
- `db_session` - Database session for each test

### API Fixtures
- `client` - FastAPI TestClient

### Sample Data Fixtures
- `sample_user_data` - User registration data
- `sample_article_data` - Article data
- `mock_llm_response` - Mock LLM response
- `mock_embedding` - Mock embedding vector

### Usage Example
```python
def test_create_user(client, sample_user_data):
    response = client.post("/auth/signup", json=sample_user_data)
    assert response.status_code == 201
    assert response.json()["email"] == sample_user_data["email"]
```

## Writing Tests

### Good Test Structure

Follow the **Arrange-Act-Assert** pattern:

```python
def test_example():
    # Arrange: Set up test data and mocks
    user_data = {"email": "test@example.com"}

    # Act: Execute the code under test
    result = create_user(user_data)

    # Assert: Verify the expected outcome
    assert result.email == "test@example.com"
```

### Test Naming Convention

- Use descriptive names: `test_<what>_<condition>_<expected>`
- Examples:
  - `test_create_user_with_valid_data_returns_201`
  - `test_login_with_invalid_password_returns_401`
  - `test_llm_provider_with_missing_api_key_raises_error`

### Async Tests

Use `@pytest.mark.asyncio` for async tests:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected
```

### Mocking External Services

Always mock external services in unit/integration tests:

```python
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_ollama_generate():
    client = OllamaClient()

    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {"message": {"content": "Test"}}
        mock_post.return_value = mock_response

        result = await client.generate("Test prompt")
        assert result == "Test"
```

### Parametrized Tests

Test multiple cases efficiently:

```python
@pytest.mark.parametrize("provider,expected_class", [
    ("ollama", OllamaClient),
    ("groq", GroqClient),
])
def test_factory_creates_correct_client(provider, expected_class):
    with patch.dict(os.environ, {"LLM_PROVIDER": provider}):
        client = LLMFactory.create_client()
        assert isinstance(client, expected_class)
```

## Test Data

### Using Fixtures

Store reusable test data in `tests/fixtures/`:

```python
# tests/fixtures/sample_articles.json
[
  {
    "title": "OpenAI Announces GPT-5",
    "source_url": "https://openai.com/blog/gpt-5",
    "companies": ["openai"]
  }
]
```

Load in tests:
```python
import json

@pytest.fixture
def sample_articles():
    with open("tests/fixtures/sample_articles.json") as f:
        return json.load(f)
```

## CI/CD Integration

Tests run automatically on:
- Every commit (unit tests)
- Every pull request (unit + integration)
- Before deployment (all tests)

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run unit tests
        run: pytest tests/unit/ -v
```

## Coverage Goals

- **Overall**: > 80%
- **Critical paths**: > 95% (auth, payment, core business logic)
- **Utilities**: > 90%

Check coverage:
```bash
pytest --cov=api --cov-report=term-missing
```

## Troubleshooting

### Tests Hang
- Check if Ollama is running when using `@pytest.mark.requires_ollama`
- Ensure Docker services are up for integration tests

### Database Errors
- Integration tests use in-memory SQLite by default
- Ensure migrations are up to date

### Import Errors
```bash
# Ensure you're in backend directory
cd backend

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Slow Tests
```bash
# Skip slow tests during development
pytest -m "not slow"

# Run only fast unit tests
pytest tests/unit/ -m "not slow"
```

## Best Practices

1. **Keep tests independent**: Each test should set up and tear down its own data
2. **Mock external services**: Don't call real APIs in tests
3. **Use descriptive names**: Test name should explain what it tests
4. **Test edge cases**: Not just happy path
5. **Keep tests fast**: Unit tests should be < 1 second
6. **One assertion per test** (when possible): Makes failures easier to diagnose
7. **Use fixtures**: Avoid duplicating test setup code

## Examples

See example tests:
- `tests/unit/test_llm_provider.py` - Complete unit test example
- More examples coming as features are implemented

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
