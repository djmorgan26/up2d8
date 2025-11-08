import pytest
from unittest.mock import MagicMock

def test_create_user_new_user(test_client, mocker):
    client, mock_db_client = test_client # Unpack the fixture
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection # Configure the mock db client
    mock_users_collection.find_one.return_value = None

    response = client.post("/api/users", json={"email": "new@example.com", "topics": ["tech"]})
    assert response.status_code == 200
    assert response.json()["message"] == "Subscription confirmed."
    assert "user_id" in response.json()
    mock_users_collection.insert_one.assert_called_once()
    assert mock_users_collection.insert_one.call_args[0][0]["email"] == "new@example.com"

def test_create_user_existing_user(test_client, mocker):
    client, mock_db_client = test_client # Unpack the fixture
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection # Configure the mock db client
    mock_users_collection.find_one.return_value = {"user_id": "existing_id", "email": "existing@example.com", "topics": ["old_topic"]}
    mock_users_collection.update_one.return_value.modified_count = 1

    response = client.post("/api/users", json={"email": "existing@example.com", "topics": ["new_topic"]})
    assert response.status_code == 200
    assert response.json()["message"] == "User already exists, topics updated."
    assert response.json()["user_id"] == "existing_id"
    mock_users_collection.update_one.assert_called_once()
    assert "$addToSet" in mock_users_collection.update_one.call_args[0][1]

def test_update_user_success(test_client, mocker):
    client, mock_db_client = test_client # Unpack the fixture
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection # Configure the mock db client
    mock_users_collection.update_one.return_value.matched_count = 1

    user_id = "some_user_id"
    response = client.put(f"/api/users/{user_id}", json={"topics": ["updated_topic"], "preferences": {"theme": "dark"}})
    assert response.status_code == 200
    assert response.json()["message"] == "Preferences updated."
    mock_users_collection.update_one.assert_called_once()
    assert mock_users_collection.update_one.call_args[0][0]["user_id"] == user_id
    assert "$set" in mock_users_collection.update_one.call_args[0][1]

def test_update_user_not_found(test_client, mocker):
    client, mock_db_client = test_client # Unpack the fixture
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection # Configure the mock db client
    mock_users_collection.update_one.return_value.matched_count = 0

    user_id = "non_existent_id"
    response = client.put(f"/api/users/{user_id}", json={"topics": ["any_topic"]})
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."
    mock_users_collection.update_one.assert_called_once()

def test_update_user_partial_update_topics(test_client, mocker):
    client, mock_db_client = test_client # Unpack the fixture
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection # Configure the mock db client
    mock_users_collection.update_one.return_value.matched_count = 1

    user_id = "some_user_id"
    response = client.put(f"/api/users/{user_id}", json={"topics": ["only_topics"]})
    assert response.status_code == 200
    assert response.json()["message"] == "Preferences updated."
    mock_users_collection.update_one.assert_called_once()
    update_payload = mock_users_collection.update_one.call_args[0][1]["$set"]
    assert "topics" in update_payload
    assert "preferences" not in update_payload

def test_update_user_partial_update_preferences(test_client, mocker):
    client, mock_db_client = test_client # Unpack the fixture
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection # Configure the mock db client
    mock_users_collection.update_one.return_value.matched_count = 1

    user_id = "some_user_id"
    response = client.put(f"/api/users/{user_id}", json={"preferences": {"lang": "en"}})
    assert response.status_code == 200
    assert response.json()["message"] == "Preferences updated."
    mock_users_collection.update_one.assert_called_once()
    update_payload = mock_users_collection.update_one.call_args[0][1]["$set"]
    assert "preferences" in update_payload
    assert "topics" not in update_payload

def test_update_user_no_fields_to_update(test_client, mocker):
    client, mock_db_client = test_client # Unpack the fixture
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection # Configure the mock db client

    user_id = "some_user_id"
    response = client.put(f"/api/users/{user_id}", json={})
    assert response.status_code == 400
    assert response.json()["detail"] == "No fields to update provided."
    mock_users_collection.update_one.assert_not_called()
