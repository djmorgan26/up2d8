from unittest.mock import MagicMock

from auth import User, get_current_user
from main import app


def test_create_user_new_user(test_client, mocker):
    client, mock_db_client = test_client
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection
    mock_users_collection.find_one.return_value = None  # No user found by id or email

    # Mock the get_current_user dependency
    mock_user = User(sub="new_user_sub", email="new@example.com", name="New User")
    app.dependency_overrides[get_current_user] = lambda: mock_user

    response = client.post("/api/users", json={"topics": ["tech"]})

    assert response.status_code == 200
    assert response.json()["message"] == "New user created."
    assert response.json()["user_id"] == "new_user_sub"
    mock_users_collection.insert_one.assert_called_once()
    inserted_user = mock_users_collection.insert_one.call_args[0][0]
    assert inserted_user["email"] == "new@example.com"
    assert inserted_user["user_id"] == "new_user_sub"

    # Clean up dependency override
    app.dependency_overrides = {}


def test_create_user_existing_user_by_id(test_client, mocker):
    client, mock_db_client = test_client
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection

    # User is found by user_id
    mock_users_collection.find_one.return_value = {
        "user_id": "existing_sub",
        "email": "existing@example.com",
        "topics": ["old_topic"],
    }

    # Mock the get_current_user dependency
    mock_user = User(sub="existing_sub", email="existing@example.com", name="Existing User")
    app.dependency_overrides[get_current_user] = lambda: mock_user

    response = client.post("/api/users", json={"topics": ["new_topic"]})

    assert response.status_code == 200
    assert response.json()["message"] == "User topics updated."
    assert response.json()["user_id"] == "existing_sub"
    mock_users_collection.update_one.assert_called_once()
    update_filter = mock_users_collection.update_one.call_args[0][0]
    update_data = mock_users_collection.update_one.call_args[0][1]
    assert update_filter["user_id"] == "existing_sub"
    assert "$addToSet" in update_data

    # Clean up dependency override
    app.dependency_overrides = {}


def test_create_user_existing_user_by_email_migration(test_client, mocker):
    client, mock_db_client = test_client
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection

    # First find_one (by id) returns None, second find_one (by email) returns the user
    mock_users_collection.find_one.side_effect = [
        None,
        {"email": "legacy@example.com", "topics": ["old_topic"]},
    ]

    # Mock the get_current_user dependency
    mock_user = User(sub="new_sub_for_legacy_user", email="legacy@example.com", name="Legacy User")
    app.dependency_overrides[get_current_user] = lambda: mock_user

    response = client.post("/api/users", json={"topics": ["new_topic"]})

    assert response.status_code == 200
    assert response.json()["message"] == "User account linked and topics updated."
    assert response.json()["user_id"] == "new_sub_for_legacy_user"
    mock_users_collection.update_one.assert_called_once()
    update_filter = mock_users_collection.update_one.call_args[0][0]
    update_data = mock_users_collection.update_one.call_args[0][1]
    assert update_filter["email"] == "legacy@example.com"
    assert update_data["$set"]["user_id"] == "new_sub_for_legacy_user"

    # Clean up dependency override
    app.dependency_overrides = {}


def test_update_user_success(test_client, mocker):
    client, mock_db_client = test_client  # Unpack the fixture
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection  # Configure the mock db client
    mock_users_collection.update_one.return_value.matched_count = 1

    user_id = "some_user_id"
    response = client.put(
        f"/api/users/{user_id}",
        json={"topics": ["updated_topic"], "preferences": {"theme": "dark"}},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Preferences updated."
    mock_users_collection.update_one.assert_called_once()
    assert mock_users_collection.update_one.call_args[0][0]["user_id"] == user_id
    assert "$set" in mock_users_collection.update_one.call_args[0][1]


def test_update_user_not_found(test_client, mocker):
    client, mock_db_client = test_client  # Unpack the fixture
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection  # Configure the mock db client
    mock_users_collection.update_one.return_value.matched_count = 0

    user_id = "non_existent_id"
    response = client.put(f"/api/users/{user_id}", json={"topics": ["any_topic"]})
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."
    mock_users_collection.update_one.assert_called_once()


def test_update_user_partial_update_topics(test_client, mocker):
    client, mock_db_client = test_client  # Unpack the fixture
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection  # Configure the mock db client
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
    client, mock_db_client = test_client  # Unpack the fixture
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection  # Configure the mock db client
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
    client, mock_db_client = test_client  # Unpack the fixture
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection  # Configure the mock db client

    user_id = "some_user_id"
    response = client.put(f"/api/users/{user_id}", json={})
    assert response.status_code == 400
    assert response.json()["detail"] == "No fields to update provided."
    mock_users_collection.update_one.assert_not_called()
