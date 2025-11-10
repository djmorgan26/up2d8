from unittest.mock import MagicMock


def test_create_feedback(test_client, mocker):
    client, mock_db_client = test_client  # Unpack the fixture
    mock_feedback_collection = MagicMock()
    mock_db_client.feedback = mock_feedback_collection  # Configure the mock db client

    feedback_data = {
        "message_id": "550e8400-e29b-41d4-a716-446655440000",  # Valid UUID format
        "user_id": "550e8400-e29b-41d4-a716-446655440001",  # Valid UUID format
        "rating": "positive"  # Valid rating from allowed list
    }
    response = client.post("/api/feedback", json=feedback_data)  # Use the unpacked client

    assert response.status_code == 201
    assert response.json()["message"] == "Feedback received."
    mock_feedback_collection.insert_one.assert_called_once()
    inserted_feedback = mock_feedback_collection.insert_one.call_args[0][0]
    assert inserted_feedback["message_id"] == "550e8400-e29b-41d4-a716-446655440000"
    assert inserted_feedback["user_id"] == "550e8400-e29b-41d4-a716-446655440001"
    assert inserted_feedback["rating"] == "positive"
    assert "timestamp" in inserted_feedback


def test_create_feedback_invalid_data(test_client):
    client, _ = test_client  # Unpack the fixture, _ for unused mock_db_client
    response = client.post("/api/feedback", json={"message_id": "msg123", "user_id": "user456"})
    assert response.status_code == 422
