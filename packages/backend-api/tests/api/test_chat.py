import pytest
from unittest.mock import MagicMock

def test_chat_endpoint(test_client, mocker):
    client, _ = test_client # Unpack the fixture, _ for unused mock_db_client
    mock_generative_model = MagicMock()
    mocker.patch('google.generativeai.GenerativeModel', return_value=mock_generative_model)
    mock_generative_model.generate_content.return_value.text = "Mocked Gemini Response"

    response = client.post("/api/chat", json={"prompt": "Hello Gemini"}) # Use the unpacked client
    assert response.status_code == 200
    assert response.json()["text"] == "Mocked Gemini Response"
    mock_generative_model.generate_content.assert_called_once_with("Hello Gemini")

def test_create_session(test_client, mocker):
    client, mock_db_client = test_client # Unpack the fixture
    mock_sessions_collection = MagicMock()
    mock_db_client.sessions = mock_sessions_collection # Configure the mock db client

    response = client.post("/api/sessions", json={"user_id": "test_user", "title": "Test Session"})
    assert response.status_code == 200
    assert "session_id" in response.json()
    mock_sessions_collection.insert_one.assert_called_once()
    inserted_session = mock_sessions_collection.insert_one.call_args[0][0]
    assert inserted_session["user_id"] == "test_user"
    assert inserted_session["title"] == "Test Session"
    assert "created_at" in inserted_session
    assert inserted_session["messages"] == []

def test_get_sessions_for_user(test_client, mocker):
    client, mock_db_client = test_client # Unpack the fixture
    mock_sessions_collection = MagicMock()
    mock_db_client.sessions = mock_sessions_collection # Configure the mock db client
    mock_sessions_collection.find.return_value = [
        {"session_id": "session1", "user_id": "user1", "title": "Session 1", "created_at": "2023-01-01T00:00:00Z"},
        {"session_id": "session2", "user_id": "user1", "title": "Session 2", "created_at": "2023-01-02T00:00:00Z"}
    ]

    response = client.get("/api/users/user1/sessions")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["session_id"] == "session1"
    mock_sessions_collection.find.assert_called_once_with({"user_id": "user1"}, {"_id": 0})

def test_send_message_to_session(test_client, mocker):
    client, mock_db_client = test_client # Unpack the fixture
    mock_sessions_collection = MagicMock()
    mock_db_client.sessions = mock_sessions_collection # Configure the mock db client
    mock_sessions_collection.update_one.return_value.matched_count = 1

    session_id = "test_session_id"
    response = client.post(f"/api/sessions/{session_id}/messages", json={"content": "Hello from test"})
    assert response.status_code == 200
    assert response.json()["message"] == "Message sent."
    mock_sessions_collection.update_one.assert_called_once()
    update_filter = mock_sessions_collection.update_one.call_args[0][0]
    update_payload = mock_sessions_collection.update_one.call_args[0][1]
    assert update_filter["session_id"] == session_id
    assert "$push" in update_payload
    assert update_payload["$push"]["messages"]["role"] == "user"
    assert update_payload["$push"]["messages"]["content"] == "Hello from test"

def test_send_message_session_not_found(test_client, mocker):
    client, mock_db_client = test_client # Unpack the fixture
    mock_sessions_collection = MagicMock()
    mock_db_client.sessions = mock_sessions_collection # Configure the mock db client
    mock_sessions_collection.update_one.return_value.matched_count = 0

    session_id = "non_existent_session"
    response = client.post(f"/api/sessions/{session_id}/messages", json={"content": "Hello"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found."

def test_get_messages_from_session(test_client, mocker):
    client, mock_db_client = test_client # Unpack the fixture
    mock_sessions_collection = MagicMock()
    mock_db_client.sessions = mock_sessions_collection # Configure the mock db client
    mock_sessions_collection.find_one.return_value = {
        "session_id": "session1",
        "messages": [
            {"role": "user", "content": "Hi"},
            {"role": "model", "content": "Hello there"}
        ]
    }

    session_id = "session1"
    response = client.get(f"/api/sessions/{session_id}/messages")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["content"] == "Hi"
    mock_sessions_collection.find_one.assert_called_once_with({"session_id": session_id}, {"_id": 0, "messages": 1})

def test_get_messages_session_not_found(test_client, mocker):
    client, mock_db_client = test_client # Unpack the fixture
    mock_sessions_collection = MagicMock()
    mock_db_client.sessions = mock_sessions_collection # Configure the mock db client
    mock_sessions_collection.find_one.return_value = None

    session_id = "non_existent_session"
    response = client.get(f"/api/sessions/{session_id}/messages")
    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found."