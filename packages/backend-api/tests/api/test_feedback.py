import pytest
from unittest.mock import MagicMock

def test_create_feedback(test_client, mocker):
    client, mock_db_client = test_client # Unpack the fixture
    mock_feedback_collection = MagicMock()
    mock_db_client.feedback = mock_feedback_collection # Configure the mock db client

    feedback_data = {"message_id": "msg123", "user_id": "user456", "rating": "good"}
    response = client.post("/api/feedback", json=feedback_data) # Use the unpacked client

    assert response.status_code == 201
    assert response.json()["message"] == "Feedback received."
    mock_feedback_collection.insert_one.assert_called_once()
    inserted_feedback = mock_feedback_collection.insert_one.call_args[0][0]
    assert inserted_feedback["message_id"] == "msg123"
    assert inserted_feedback["user_id"] == "user456"
    assert inserted_feedback["rating"] == "good"
    assert "timestamp" in inserted_feedback

def test_create_feedback_invalid_data(test_client):
    client, _ = test_client # Unpack the fixture, _ for unused mock_db_client
    response = client.post("/api/feedback", json={"message_id": "msg123", "user_id": "user456"})
    assert response.status_code == 422