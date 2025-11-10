from unittest.mock import MagicMock

from dependencies import get_db_client
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check_healthy():
    """Test health check endpoint when database is healthy"""
    mock_db_client = MagicMock()
    mock_db_client.command.return_value = {"ok": 1}  # Successful ping
    mock_db_client.articles.count_documents.side_effect = [100, 10]  # total, unprocessed
    mock_db_client.users.count_documents.return_value = 50
    mock_db_client.rss_feeds.count_documents.return_value = 25

    app.dependency_overrides[get_db_client] = lambda: mock_db_client

    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"]["status"] == "connected"
    assert data["database"]["ping_ok"] == True
    assert "timestamp" in data
    assert "service" in data
    assert "version" in data
    assert data["collections"]["articles"]["total"] == 100
    assert data["collections"]["articles"]["unprocessed"] == 10
    assert data["collections"]["articles"]["processed"] == 90
    assert data["collections"]["users"] == 50
    assert data["collections"]["rss_feeds"] == 25

    # Verify database ping was called
    mock_db_client.command.assert_called_once_with("ping")

    app.dependency_overrides = {}


def test_health_check_unhealthy():
    """Test health check endpoint when database connection fails"""
    mock_db_client = MagicMock()
    mock_db_client.command.side_effect = Exception("Connection failed")

    app.dependency_overrides[get_db_client] = lambda: mock_db_client

    response = client.get("/api/health")
    assert response.status_code == 200  # Endpoint should still return 200

    data = response.json()
    assert data["status"] == "unhealthy"
    assert "error" in data
    assert "Connection failed" in data["error"]
    assert "timestamp" in data

    app.dependency_overrides = {}


def test_health_check_partial_failure():
    """Test health check when some collection counts fail"""
    mock_db_client = MagicMock()
    mock_db_client.command.return_value = {"ok": 1}
    # First count succeeds, second fails
    mock_db_client.articles.count_documents.side_effect = Exception("Count failed")

    app.dependency_overrides[get_db_client] = lambda: mock_db_client

    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "unhealthy"
    assert "error" in data

    app.dependency_overrides = {}
