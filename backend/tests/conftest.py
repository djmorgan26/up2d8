"""
Pytest configuration and shared fixtures for UP2D8 tests
"""
import pytest
import os
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["EMBEDDING_PROVIDER"] = "sentence-transformers"
os.environ["VECTOR_DB_PROVIDER"] = "chroma"
os.environ["EMAIL_PROVIDER"] = "console"


@pytest.fixture(scope="session")
def test_db_engine():
    """
    Create a test database engine using in-memory SQLite
    """
    from api.db.session import Base

    # Use in-memory SQLite for tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """
    Create a new database session for each test
    """
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_db_engine
    )

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(db_session) -> Generator:
    """
    Create a test client for API testing
    """
    from api.main import app
    from api.db.session import get_db

    # Override the get_db dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def sample_user_data():
    """
    Sample user data for testing
    """
    return {
        "email": "test@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test User"
    }


@pytest.fixture(scope="function")
def sample_article_data():
    """
    Sample article data for testing
    """
    return {
        "title": "OpenAI Announces GPT-5",
        "source_url": "https://openai.com/blog/gpt-5",
        "source_id": "openai_blog",
        "content": "OpenAI today announced GPT-5, featuring improved reasoning capabilities...",
        "published_at": "2025-10-23T14:00:00Z",
        "companies": ["openai"],
        "industries": ["ai", "technology"],
        "impact_score": 9
    }


@pytest.fixture(scope="function")
def mock_llm_response():
    """
    Mock LLM response for testing without calling real LLM
    """
    return "This is a test summary of the article."


@pytest.fixture(scope="function")
def mock_embedding():
    """
    Mock embedding vector for testing
    """
    return [0.1] * 384  # 384-dimensional vector (all-MiniLM-L6-v2 dimension)


# Async test fixtures
@pytest.fixture(scope="session")
def event_loop():
    """
    Create an event loop for async tests
    """
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Mark configurations
def pytest_configure(config):
    """
    Register custom markers
    """
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "requires_ollama: marks tests that require Ollama to be running"
    )
