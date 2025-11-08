from fastapi.testclient import TestClient
from main import app
from dependencies import get_db_client
from unittest.mock import MagicMock
import uuid

client = TestClient(app)

def test_create_rss_feed():
    mock_rss_feeds_collection = MagicMock()
    
    app.dependency_overrides[get_db_client] = lambda: MagicMock(rss_feeds=mock_rss_feeds_collection)

    response = client.post(
        "/api/rss_feeds",
        json={
            "url": "https://example.com/rss",
            "category": "Tech"
        }
    )
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["message"] == "RSS Feed created successfully."
    mock_rss_feeds_collection.insert_one.assert_called_once()

    app.dependency_overrides = {}

def test_get_rss_feeds():
    mock_rss_feeds_collection = MagicMock()
    mock_rss_feeds_collection.find.return_value = [
        {"id": "feed1", "url": "https://example.com/feed1", "category": "News"},
        {"id": "feed2", "url": "https://example.com/feed2", "category": "Sports"}
    ]
    
    app.dependency_overrides[get_db_client] = lambda: MagicMock(rss_feeds=mock_rss_feeds_collection)

    response = client.get("/api/rss_feeds")
    assert response.status_code == 200
    assert response.json() == [
        {"id": "feed1", "url": "https://example.com/feed1", "category": "News"},
        {"id": "feed2", "url": "https://example.com/feed2", "category": "Sports"}
    ]

    app.dependency_overrides = {}

def test_get_rss_feed_by_id():
    mock_rss_feeds_collection = MagicMock()
    mock_rss_feeds_collection.find_one.return_value = {"id": "feed1", "url": "https://example.com/feed1", "category": "News"}
    
    app.dependency_overrides[get_db_client] = lambda: MagicMock(rss_feeds=mock_rss_feeds_collection)

    response = client.get("/api/rss_feeds/feed1")
    assert response.status_code == 200
    assert response.json() == {"id": "feed1", "url": "https://example.com/feed1", "category": "News"}

    app.dependency_overrides = {}

def test_get_rss_feed_by_id_not_found():
    mock_rss_feeds_collection = MagicMock()
    mock_rss_feeds_collection.find_one.return_value = None
    
    app.dependency_overrides[get_db_client] = lambda: MagicMock(rss_feeds=mock_rss_feeds_collection)

    response = client.get("/api/rss_feeds/nonexistent")
    assert response.status_code == 404
    assert response.json() == {"detail": "RSS Feed not found."} 

    app.dependency_overrides = {}

def test_update_rss_feed():
    mock_rss_feeds_collection = MagicMock()
    mock_rss_feeds_collection.update_one.return_value.matched_count = 1
    
    app.dependency_overrides[get_db_client] = lambda: MagicMock(rss_feeds=mock_rss_feeds_collection)

    response = client.put(
        "/api/rss_feeds/feed1",
        json={
            "url": "https://updated.com/rss",
            "category": "Updated"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"message": "RSS Feed updated successfully."}
    mock_rss_feeds_collection.update_one.assert_called_once()

    app.dependency_overrides = {}

def test_update_rss_feed_not_found():
    mock_rss_feeds_collection = MagicMock()
    mock_rss_feeds_collection.update_one.return_value.matched_count = 0
    
    app.dependency_overrides[get_db_client] = lambda: MagicMock(rss_feeds=mock_rss_feeds_collection)

    response = client.put(
        "/api/rss_feeds/nonexistent",
        json={
            "url": "https://updated.com/rss"
        }
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "RSS Feed not found."} 

    app.dependency_overrides = {}

def test_delete_rss_feed():
    mock_rss_feeds_collection = MagicMock()
    mock_rss_feeds_collection.delete_one.return_value.deleted_count = 1
    
    app.dependency_overrides[get_db_client] = lambda: MagicMock(rss_feeds=mock_rss_feeds_collection)

    response = client.delete("/api/rss_feeds/feed1")
    assert response.status_code == 200
    assert response.json() == {"message": "RSS Feed deleted successfully."}
    mock_rss_feeds_collection.delete_one.assert_called_once()

    app.dependency_overrides = {}

def test_delete_rss_feed_not_found():
    mock_rss_feeds_collection = MagicMock()
    mock_rss_feeds_collection.delete_one.return_value.deleted_count = 0
    
    app.dependency_overrides[get_db_client] = lambda: MagicMock(rss_feeds=mock_rss_feeds_collection)

    response = client.delete("/api/rss_feeds/nonexistent")
    assert response.status_code == 404
    assert response.json() == {"detail": "RSS Feed not found."} 

    app.dependency_overrides = {}
