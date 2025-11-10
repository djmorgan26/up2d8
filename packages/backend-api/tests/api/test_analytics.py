from unittest.mock import MagicMock


def test_create_analytics(test_client, mocker):
    client, mock_db_client = test_client  # Unpack the fixture
    mock_analytics_collection = MagicMock()
    mock_db_client.analytics = mock_analytics_collection  # Configure the mock db client

    analytics_data = {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",  # Valid UUID format
        "event_type": "article_view",  # Valid event type from allowed list
        "details": {"article_id": "123", "duration_seconds": 45},
    }
    response = client.post("/api/analytics", json=analytics_data)  # Use the unpacked client

    assert response.status_code == 202
    assert response.json()["message"] == "Event logged."
    mock_analytics_collection.insert_one.assert_called_once()
    inserted_analytics = mock_analytics_collection.insert_one.call_args[0][0]
    assert inserted_analytics["user_id"] == "550e8400-e29b-41d4-a716-446655440000"
    assert inserted_analytics["event_type"] == "article_view"
    assert inserted_analytics["details"] == {"article_id": "123", "duration_seconds": 45}
    assert "timestamp" in inserted_analytics


def test_create_analytics_invalid_data(test_client):
    client, _ = test_client  # Unpack the fixture, _ for unused mock_db_client
    response = client.post("/api/analytics", json={"user_id": "user789", "event_type": "page_view"})
    assert response.status_code == 422
