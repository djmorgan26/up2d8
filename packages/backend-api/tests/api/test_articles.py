from unittest.mock import MagicMock

from dependencies import get_db_client
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_articles():
    mock_articles_collection = MagicMock()
    mock_articles_collection.find.return_value = [
        {
            "id": "article1",
            "title": "Test Article 1",
            "summary": "Summary 1",
            "link": "http://example.com/1",
            "published": "2025-11-08T12:00:00Z",
            "source": "Example",
        },
        {
            "id": "article2",
            "title": "Test Article 2",
            "summary": "Summary 2",
            "link": "http://anotherexample.com/2",
            "published": "2025-11-08T13:00:00Z",
            "source": "Another",
        },
    ]

    app.dependency_overrides[get_db_client] = lambda: MagicMock(articles=mock_articles_collection)

    response = client.get("/api/articles")
    assert response.status_code == 200
    assert response.json() == {
        "data": [
            {
                "id": "article1",
                "title": "Test Article 1",
                "description": "Summary 1",
                "url": "http://example.com/1",
                "published_at": "2025-11-08T12:00:00Z",
                "source": "Example",
            },
            {
                "id": "article2",
                "title": "Test Article 2",
                "description": "Summary 2",
                "url": "http://anotherexample.com/2",
                "published_at": "2025-11-08T13:00:00Z",
                "source": "Another",
            },
        ]
    }

    app.dependency_overrides = {}


def test_get_article_by_id():
    mock_articles_collection = MagicMock()
    mock_articles_collection.find_one.return_value = {"id": "article1", "title": "Test Article 1"}

    app.dependency_overrides[get_db_client] = lambda: MagicMock(articles=mock_articles_collection)

    response = client.get("/api/articles/article1")
    assert response.status_code == 200
    assert response.json() == {"id": "article1", "title": "Test Article 1"}

    app.dependency_overrides = {}


def test_get_article_by_id_not_found():
    mock_articles_collection = MagicMock()
    mock_articles_collection.find_one.return_value = None

    app.dependency_overrides[get_db_client] = lambda: MagicMock(articles=mock_articles_collection)

    response = client.get("/api/articles/nonexistent")
    assert response.status_code == 404
    assert response.json() == {"detail": "Article not found."}

    app.dependency_overrides = {}


def test_get_articles_empty_database():
    """Test getting articles when database is empty"""
    mock_articles_collection = MagicMock()
    mock_articles_collection.find.return_value = []

    app.dependency_overrides[get_db_client] = lambda: MagicMock(articles=mock_articles_collection)

    response = client.get("/api/articles")
    assert response.status_code == 200
    assert response.json() == {"data": []}

    app.dependency_overrides = {}


def test_get_articles_missing_fields():
    """Test getting articles when some have missing fields"""
    mock_articles_collection = MagicMock()
    mock_articles_collection.find.return_value = [
        {
            "id": "article1",
            "title": "Complete Article",
            "summary": "Summary",
            "link": "http://example.com/1",
            "published": "2025-11-08T12:00:00Z",
            "source": "Example",
        },
        {
            "id": "article2",
            "title": "Incomplete Article",
            # missing summary
            "link": "http://example.com/2",
            "published": "2025-11-08T13:00:00Z",
            # missing source
        },
    ]

    app.dependency_overrides[get_db_client] = lambda: MagicMock(articles=mock_articles_collection)

    response = client.get("/api/articles")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 2
    # First article should be complete
    assert data[0]["description"] == "Summary"
    assert data[0]["source"] == "Example"

    app.dependency_overrides = {}


def test_get_articles_with_special_characters():
    """Test articles with special characters in title/summary"""
    mock_articles_collection = MagicMock()
    mock_articles_collection.find.return_value = [
        {
            "id": "article1",
            "title": "Article with <HTML> & \"quotes\"",
            "summary": "Summary with special chars: © ™ € £",
            "link": "http://example.com/1",
            "published": "2025-11-08T12:00:00Z",
            "source": "Example",
        }
    ]

    app.dependency_overrides[get_db_client] = lambda: MagicMock(articles=mock_articles_collection)

    response = client.get("/api/articles")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert '<HTML>' in data[0]["title"]
    assert '©' in data[0]["description"]

    app.dependency_overrides = {}


def test_get_articles_database_error():
    """Test that database errors are raised when fetching articles

    Note: This test verifies that database errors are not silently swallowed.
    In production, FastAPI will catch this and return a 500 error to the client.
    """
    import pytest

    mock_articles_collection = MagicMock()
    mock_articles_collection.find.side_effect = Exception("Database connection error")

    app.dependency_overrides[get_db_client] = lambda: MagicMock(articles=mock_articles_collection)

    # Expect the exception to be raised (FastAPI will handle it in production)
    with pytest.raises(Exception, match="Database connection error"):
        client.get("/api/articles")

    app.dependency_overrides = {}


def test_get_article_with_invalid_id_format():
    """Test getting article with various invalid ID formats"""
    mock_articles_collection = MagicMock()
    mock_articles_collection.find_one.return_value = None

    app.dependency_overrides[get_db_client] = lambda: MagicMock(articles=mock_articles_collection)

    # Test with very long ID
    long_id = "a" * 1000
    response = client.get(f"/api/articles/{long_id}")
    assert response.status_code == 404

    # Test with special characters
    special_id = "article@#$%"
    response = client.get(f"/api/articles/{special_id}")
    assert response.status_code == 404

    app.dependency_overrides = {}
