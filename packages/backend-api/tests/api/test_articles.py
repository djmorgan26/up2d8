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
