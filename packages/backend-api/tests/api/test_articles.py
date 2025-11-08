from fastapi.testclient import TestClient
from main import app
from dependencies import get_db_client
from unittest.mock import MagicMock

client = TestClient(app)

def test_get_articles():
    mock_articles_collection = MagicMock()
    mock_articles_collection.find.return_value = [
        {"id": "article1", "title": "Test Article 1"},
        {"id": "article2", "title": "Test Article 2"}
    ]
    
    app.dependency_overrides[get_db_client] = lambda: MagicMock(articles=mock_articles_collection)

    response = client.get("/api/articles")
    assert response.status_code == 200
    assert response.json() == [
        {"id": "article1", "title": "Test Article 1"},
        {"id": "article2", "title": "Test Article 2"}
    ]

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
