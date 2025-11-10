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

    # Mock authentication
    from auth import User, get_current_user
    from main import app

    user_id = "some_user_id"
    mock_user = User(sub=user_id, email="test@example.com", name="Test User")
    app.dependency_overrides[get_current_user] = lambda: mock_user

    response = client.put(
        f"/api/users/{user_id}",
        json={"topics": ["updated_topic"], "preferences": {"theme": "dark"}},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Preferences updated."
    mock_users_collection.update_one.assert_called_once()
    assert mock_users_collection.update_one.call_args[0][0]["user_id"] == user_id
    assert "$set" in mock_users_collection.update_one.call_args[0][1]

    app.dependency_overrides = {}


def test_update_user_not_found(test_client, mocker):
    client, mock_db_client = test_client  # Unpack the fixture
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection  # Configure the mock db client
    mock_users_collection.update_one.return_value.matched_count = 0

    # Mock authentication
    from auth import User, get_current_user
    from main import app

    user_id = "non_existent_id"
    mock_user = User(sub=user_id, email="test@example.com", name="Test User")
    app.dependency_overrides[get_current_user] = lambda: mock_user

    response = client.put(f"/api/users/{user_id}", json={"topics": ["any_topic"]})
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."
    mock_users_collection.update_one.assert_called_once()

    app.dependency_overrides = {}


def test_update_user_partial_update_topics(test_client, mocker):
    client, mock_db_client = test_client  # Unpack the fixture
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection  # Configure the mock db client
    mock_users_collection.update_one.return_value.matched_count = 1

    # Mock authentication
    from auth import User, get_current_user
    from main import app

    user_id = "some_user_id"
    mock_user = User(sub=user_id, email="test@example.com", name="Test User")
    app.dependency_overrides[get_current_user] = lambda: mock_user

    response = client.put(f"/api/users/{user_id}", json={"topics": ["only_topics"]})
    assert response.status_code == 200
    assert response.json()["message"] == "Preferences updated."
    mock_users_collection.update_one.assert_called_once()
    update_payload = mock_users_collection.update_one.call_args[0][1]["$set"]
    assert "topics" in update_payload
    assert "preferences" not in update_payload

    app.dependency_overrides = {}


def test_update_user_partial_update_preferences(test_client, mocker):
    client, mock_db_client = test_client  # Unpack the fixture
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection  # Configure the mock db client
    mock_users_collection.update_one.return_value.matched_count = 1

    # Mock authentication
    from auth import User, get_current_user
    from main import app

    user_id = "some_user_id"
    mock_user = User(sub=user_id, email="test@example.com", name="Test User")
    app.dependency_overrides[get_current_user] = lambda: mock_user

    response = client.put(f"/api/users/{user_id}", json={"preferences": {"lang": "en"}})
    assert response.status_code == 200
    assert response.json()["message"] == "Preferences updated."
    mock_users_collection.update_one.assert_called_once()
    update_payload = mock_users_collection.update_one.call_args[0][1]["$set"]
    assert "preferences" in update_payload
    assert "topics" not in update_payload

    app.dependency_overrides = {}


def test_update_user_no_fields_to_update(test_client, mocker):
    client, mock_db_client = test_client  # Unpack the fixture
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection  # Configure the mock db client

    # Mock authentication
    from auth import User, get_current_user
    from main import app

    user_id = "some_user_id"
    mock_user = User(sub=user_id, email="test@example.com", name="Test User")
    app.dependency_overrides[get_current_user] = lambda: mock_user

    response = client.put(f"/api/users/{user_id}", json={})
    assert response.status_code == 400
    assert response.json()["detail"] == "No fields to update provided."
    mock_users_collection.update_one.assert_not_called()

    app.dependency_overrides = {}


def test_get_current_user_info(test_client):
    """Test GET /api/users/me endpoint."""
    client, mock_db_client = test_client
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection

    # Mock user data in database
    mock_users_collection.find_one.return_value = {
        "user_id": "test_user_123",
        "email": "test@example.com",
        "topics": ["AI", "Tech"],
        "preferences": {"theme": "dark"},
        "created_at": "2025-01-01T00:00:00Z"
    }

    # Mock authentication
    mock_user = User(sub="test_user_123", email="test@example.com", name="Test User")
    app.dependency_overrides[get_current_user] = lambda: mock_user

    response = client.get("/api/users/me")

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "test_user_123"
    assert data["email"] == "test@example.com"
    assert data["topics"] == ["AI", "Tech"]
    assert data["preferences"] == {"theme": "dark"}

    app.dependency_overrides = {}


def test_get_current_user_info_not_in_db(test_client):
    """Test GET /api/users/me when user is authenticated but not in database."""
    client, mock_db_client = test_client
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection

    # User not found in database
    mock_users_collection.find_one.return_value = None

    # Mock authentication
    mock_user = User(sub="new_user_123", email="new@example.com", name="New User")
    app.dependency_overrides[get_current_user] = lambda: mock_user

    response = client.get("/api/users/me")

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "new_user_123"
    assert data["email"] == "new@example.com"
    assert data["topics"] == []
    assert data["preferences"] == {}
    assert data["created_at"] is None

    app.dependency_overrides = {}


def test_update_user_preferences(test_client):
    """Test PATCH /api/users/me/preferences endpoint."""
    client, mock_db_client = test_client
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection
    mock_users_collection.update_one.return_value.matched_count = 1

    # Mock authentication
    mock_user = User(sub="test_user_123", email="test@example.com", name="Test User")
    app.dependency_overrides[get_current_user] = lambda: mock_user

    response = client.patch(
        "/api/users/me/preferences",
        json={"preferences": {"theme": "light", "language": "en"}}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Preferences updated successfully."
    mock_users_collection.update_one.assert_called_once()

    # Verify the update call
    update_filter = mock_users_collection.update_one.call_args[0][0]
    update_data = mock_users_collection.update_one.call_args[0][1]
    assert update_filter["user_id"] == "test_user_123"
    assert update_data["$set"]["preferences"] == {"theme": "light", "language": "en"}

    app.dependency_overrides = {}


def test_update_user_preferences_not_found(test_client):
    """Test PATCH /api/users/me/preferences when user not found."""
    client, mock_db_client = test_client
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection
    mock_users_collection.update_one.return_value.matched_count = 0

    # Mock authentication
    mock_user = User(sub="test_user_123", email="test@example.com", name="Test User")
    app.dependency_overrides[get_current_user] = lambda: mock_user

    response = client.patch(
        "/api/users/me/preferences",
        json={"preferences": {"theme": "light"}}
    )

    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]

    app.dependency_overrides = {}


def test_add_topic(test_client):
    """Test POST /api/users/me/topics endpoint."""
    client, mock_db_client = test_client
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection
    mock_users_collection.update_one.return_value.matched_count = 1

    # Mock authentication
    mock_user = User(sub="test_user_123", email="test@example.com", name="Test User")
    app.dependency_overrides[get_current_user] = lambda: mock_user

    response = client.post(
        "/api/users/me/topics",
        json={"topic": "Machine Learning"}
    )

    assert response.status_code == 200
    assert "Machine Learning" in response.json()["message"]
    mock_users_collection.update_one.assert_called_once()

    # Verify the update call uses $addToSet
    update_filter = mock_users_collection.update_one.call_args[0][0]
    update_data = mock_users_collection.update_one.call_args[0][1]
    assert update_filter["user_id"] == "test_user_123"
    assert update_data["$addToSet"]["topics"] == "Machine Learning"

    app.dependency_overrides = {}


def test_add_topic_user_not_found(test_client):
    """Test POST /api/users/me/topics when user not found."""
    client, mock_db_client = test_client
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection
    mock_users_collection.update_one.return_value.matched_count = 0

    # Mock authentication
    mock_user = User(sub="test_user_123", email="test@example.com", name="Test User")
    app.dependency_overrides[get_current_user] = lambda: mock_user

    response = client.post(
        "/api/users/me/topics",
        json={"topic": "Machine Learning"}
    )

    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]

    app.dependency_overrides = {}


def test_remove_topic(test_client):
    """Test DELETE /api/users/me/topics endpoint."""
    client, mock_db_client = test_client
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection
    mock_users_collection.update_one.return_value.matched_count = 1

    # Mock authentication
    mock_user = User(sub="test_user_123", email="test@example.com", name="Test User")
    app.dependency_overrides[get_current_user] = lambda: mock_user

    response = client.delete("/api/users/me/topics/Old%20Topic")

    assert response.status_code == 200
    assert "Old Topic" in response.json()["message"]
    mock_users_collection.update_one.assert_called_once()

    # Verify the update call uses $pull
    update_filter = mock_users_collection.update_one.call_args[0][0]
    update_data = mock_users_collection.update_one.call_args[0][1]
    assert update_filter["user_id"] == "test_user_123"
    assert update_data["$pull"]["topics"] == "Old Topic"

    app.dependency_overrides = {}


def test_delete_user_own_account(test_client):
    """Test DELETE /api/users/{user_id} - user deletes their own account."""
    client, mock_db_client = test_client
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection
    mock_users_collection.delete_one.return_value.deleted_count = 1

    # Mock authentication
    user_id = "test_user_123"
    mock_user = User(sub=user_id, email="test@example.com", name="Test User")
    app.dependency_overrides[get_current_user] = lambda: mock_user

    response = client.delete(f"/api/users/{user_id}")

    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
    mock_users_collection.delete_one.assert_called_once()

    # Verify correct user was deleted
    delete_filter = mock_users_collection.delete_one.call_args[0][0]
    assert delete_filter["user_id"] == user_id

    app.dependency_overrides = {}


def test_delete_user_forbidden(test_client):
    """Test DELETE /api/users/{user_id} - user tries to delete another user's account."""
    client, mock_db_client = test_client
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection

    # Mock authentication - authenticated as user_123
    mock_user = User(sub="user_123", email="test@example.com", name="Test User")
    app.dependency_overrides[get_current_user] = lambda: mock_user

    # Try to delete different user (user_456)
    response = client.delete("/api/users/user_456")

    assert response.status_code == 403
    assert "only delete your own account" in response.json()["detail"]
    mock_users_collection.delete_one.assert_not_called()

    app.dependency_overrides = {}


def test_delete_user_not_found(test_client):
    """Test DELETE /api/users/{user_id} - user not found in database."""
    client, mock_db_client = test_client
    mock_users_collection = MagicMock()
    mock_db_client.users = mock_users_collection
    mock_users_collection.delete_one.return_value.deleted_count = 0

    # Mock authentication
    user_id = "test_user_123"
    mock_user = User(sub=user_id, email="test@example.com", name="Test User")
    app.dependency_overrides[get_current_user] = lambda: mock_user

    response = client.delete(f"/api/users/{user_id}")

    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]

    app.dependency_overrides = {}
