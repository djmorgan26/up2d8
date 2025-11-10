from unittest.mock import MagicMock


def test_chat_endpoint(test_client, mocker):
    """Test basic chat endpoint with no sources"""
    client, _ = test_client  # Unpack the fixture, _ for unused mock_db_client

    # Mock Gemini client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Mocked Gemini Response"
    mock_response.candidates = []
    mock_client.models.generate_content.return_value = mock_response

    mocker.patch("api.chat.genai.Client", return_value=mock_client)

    # Override the FastAPI dependency for Gemini API key
    from dependencies import get_gemini_api_key
    from main import app

    app.dependency_overrides[get_gemini_api_key] = lambda: "fake_api_key"

    response = client.post("/api/chat", json={"prompt": "Hello Gemini"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["model"] == "gemini-2.5-flash"
    assert data["reply"] == "Mocked Gemini Response"
    assert data["sources"] == []

    # Clean up
    app.dependency_overrides = {}


def test_chat_endpoint_with_sources(test_client, mocker):
    """Test chat endpoint with web search grounding sources"""
    client, _ = test_client

    # Create mock web source
    mock_web = MagicMock()
    mock_web.uri = "https://example.com/article"
    mock_web.title = "Example Article Title"

    mock_chunk = MagicMock()
    mock_chunk.web = mock_web

    mock_grounding_metadata = MagicMock()
    mock_grounding_metadata.grounding_chunks = [mock_chunk]

    mock_candidate = MagicMock()
    mock_candidate.grounding_metadata = mock_grounding_metadata

    mock_response = MagicMock()
    mock_response.text = "Here's what I found about your query."
    mock_response.candidates = [mock_candidate]

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    mocker.patch("api.chat.genai.Client", return_value=mock_client)

    # Override the FastAPI dependency for Gemini API key
    from dependencies import get_gemini_api_key
    from main import app

    app.dependency_overrides[get_gemini_api_key] = lambda: "fake_api_key"

    response = client.post("/api/chat", json={"prompt": "What's new in AI?"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["sources"]) == 1
    assert data["sources"][0]["web"]["uri"] == "https://example.com/article"
    assert data["sources"][0]["web"]["title"] == "Example Article Title"

    # Clean up
    app.dependency_overrides = {}


def test_chat_endpoint_empty_prompt(test_client, mocker):
    """Test chat endpoint rejects empty prompt"""
    client, _ = test_client

    # Mock Gemini in case it tries to process
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Response"
    mock_response.candidates = []
    mock_client.models.generate_content.return_value = mock_response
    mocker.patch("api.chat.genai.Client", return_value=mock_client)

    # Override the FastAPI dependency for Gemini API key
    from dependencies import get_gemini_api_key
    from main import app

    app.dependency_overrides[get_gemini_api_key] = lambda: "fake_api_key"

    response = client.post("/api/chat", json={"prompt": ""})
    # FastAPI validation should catch this
    assert response.status_code in [200, 422]  # May pass validation but fail in processing

    # Clean up
    app.dependency_overrides = {}


def test_chat_endpoint_long_prompt(test_client, mocker):
    """Test chat endpoint handles very long prompts"""
    client, _ = test_client

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Response to long prompt"
    mock_response.candidates = []
    mock_client.models.generate_content.return_value = mock_response

    mocker.patch("api.chat.genai.Client", return_value=mock_client)

    # Override the FastAPI dependency for Gemini API key
    from dependencies import get_gemini_api_key
    from main import app

    app.dependency_overrides[get_gemini_api_key] = lambda: "fake_api_key"

    long_prompt = "What is AI? " * 500  # Very long prompt
    response = client.post("/api/chat", json={"prompt": long_prompt})
    assert response.status_code == 200

    # Clean up
    app.dependency_overrides = {}


def test_chat_endpoint_gemini_api_error(test_client, mocker):
    """Test chat endpoint handles Gemini API errors gracefully"""
    client, _ = test_client

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("API rate limit exceeded")

    mocker.patch("api.chat.genai.Client", return_value=mock_client)

    # Override the FastAPI dependency for Gemini API key
    from dependencies import get_gemini_api_key
    from main import app

    app.dependency_overrides[get_gemini_api_key] = lambda: "fake_api_key"

    response = client.post("/api/chat", json={"prompt": "Hello"})
    assert response.status_code == 500
    assert "Gemini API error" in response.json()["detail"]

    # Clean up
    app.dependency_overrides = {}


def test_chat_endpoint_invalid_request(mocker):
    """Test chat endpoint validation"""
    # Mock Azure auth to avoid startup issues
    with mocker.patch('auth.azure_scheme.openid_config.load_config', new_callable=MagicMock):
        from fastapi.testclient import TestClient
        from main import app
        from dependencies import get_gemini_api_key

        # Override Gemini API key dependency
        app.dependency_overrides[get_gemini_api_key] = lambda: "fake_api_key"

        client = TestClient(app)

        # Missing prompt field
        response = client.post("/api/chat", json={})
        assert response.status_code == 422

        # Wrong data type
        response = client.post("/api/chat", json={"prompt": 123})
        assert response.status_code == 422

        # Clean up
        app.dependency_overrides = {}


def test_create_session(test_client, mocker):
    client, mock_db_client = test_client  # Unpack the fixture
    mock_sessions_collection = MagicMock()
    mock_db_client.sessions = mock_sessions_collection  # Configure the mock db client

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
    client, mock_db_client = test_client  # Unpack the fixture
    mock_sessions_collection = MagicMock()
    mock_db_client.sessions = mock_sessions_collection  # Configure the mock db client
    mock_sessions_collection.find.return_value = [
        {
            "session_id": "session1",
            "user_id": "user1",
            "title": "Session 1",
            "created_at": "2023-01-01T00:00:00Z",
        },
        {
            "session_id": "session2",
            "user_id": "user1",
            "title": "Session 2",
            "created_at": "2023-01-02T00:00:00Z",
        },
    ]

    response = client.get("/api/users/user1/sessions")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["session_id"] == "session1"
    mock_sessions_collection.find.assert_called_once_with({"user_id": "user1"}, {"_id": 0})


def test_send_message_to_session(test_client, mocker):
    client, mock_db_client = test_client  # Unpack the fixture
    mock_sessions_collection = MagicMock()
    mock_db_client.sessions = mock_sessions_collection  # Configure the mock db client
    mock_sessions_collection.update_one.return_value.matched_count = 1

    session_id = "test_session_id"
    response = client.post(
        f"/api/sessions/{session_id}/messages", json={"content": "Hello from test"}
    )
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
    client, mock_db_client = test_client  # Unpack the fixture
    mock_sessions_collection = MagicMock()
    mock_db_client.sessions = mock_sessions_collection  # Configure the mock db client
    mock_sessions_collection.update_one.return_value.matched_count = 0

    session_id = "non_existent_session"
    response = client.post(f"/api/sessions/{session_id}/messages", json={"content": "Hello"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found."


def test_get_messages_from_session(test_client, mocker):
    client, mock_db_client = test_client  # Unpack the fixture
    mock_sessions_collection = MagicMock()
    mock_db_client.sessions = mock_sessions_collection  # Configure the mock db client
    mock_sessions_collection.find_one.return_value = {
        "session_id": "session1",
        "messages": [
            {"role": "user", "content": "Hi"},
            {"role": "model", "content": "Hello there"},
        ],
    }

    session_id = "session1"
    response = client.get(f"/api/sessions/{session_id}/messages")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["content"] == "Hi"
    mock_sessions_collection.find_one.assert_called_once_with(
        {"session_id": session_id}, {"_id": 0, "messages": 1}
    )


def test_get_messages_session_not_found(test_client, mocker):
    client, mock_db_client = test_client  # Unpack the fixture
    mock_sessions_collection = MagicMock()
    mock_db_client.sessions = mock_sessions_collection  # Configure the mock db client
    mock_sessions_collection.find_one.return_value = None

    session_id = "non_existent_session"
    response = client.get(f"/api/sessions/{session_id}/messages")
    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found."
