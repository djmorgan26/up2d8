from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_suggest_topics_with_query(mocker):
    """Test topic suggestions based on a search query"""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Artificial Intelligence, Machine Learning, Deep Learning, Neural Networks, Computer Vision"
    mock_client.models.generate_content.return_value = mock_response

    mocker.patch("api.topics.genai.Client", return_value=mock_client)
    mocker.patch("api.topics.get_gemini_api_key", return_value="fake_api_key")

    response = client.post("/api/topics/suggest", json={"query": "AI technology", "interests": []})

    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert len(data["suggestions"]) == 5
    assert "Artificial Intelligence" in data["suggestions"]
    assert "Machine Learning" in data["suggestions"]

    # Verify Gemini was called with correct prompt
    mock_client.models.generate_content.assert_called_once()
    call_kwargs = mock_client.models.generate_content.call_args[1]
    assert "AI technology" in call_kwargs["contents"]


def test_suggest_topics_with_interests(mocker):
    """Test topic suggestions based on existing user interests"""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Data Science, Analytics, Statistics, Python Programming"
    mock_client.models.generate_content.return_value = mock_response

    mocker.patch("api.topics.genai.Client", return_value=mock_client)
    mocker.patch("api.topics.get_gemini_api_key", return_value="fake_api_key")

    response = client.post(
        "/api/topics/suggest", json={"interests": ["Technology", "Science"], "query": ""}
    )

    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert len(data["suggestions"]) == 4
    assert "Data Science" in data["suggestions"]

    # Verify prompt includes user interests
    call_kwargs = mock_client.models.generate_content.call_args[1]
    assert "Technology" in call_kwargs["contents"]
    assert "Science" in call_kwargs["contents"]


def test_suggest_topics_no_input(mocker):
    """Test topic suggestions with no query or interests (popular topics)"""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Technology, Politics, Health, Sports, Entertainment, Business, Science, World News"
    mock_client.models.generate_content.return_value = mock_response

    mocker.patch("api.topics.genai.Client", return_value=mock_client)
    mocker.patch("api.topics.get_gemini_api_key", return_value="fake_api_key")

    response = client.post("/api/topics/suggest", json={"interests": [], "query": ""})

    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert len(data["suggestions"]) == 8
    assert "Technology" in data["suggestions"]


def test_suggest_topics_with_numbered_response(mocker):
    """Test that numbered responses are cleaned up properly"""
    mock_client = MagicMock()
    mock_response = MagicMock()
    # Simulate Gemini returning numbered list despite instructions
    mock_response.text = "1. Climate Change, 2. Renewable Energy, 3. Sustainability"
    mock_client.models.generate_content.return_value = mock_response

    mocker.patch("api.topics.genai.Client", return_value=mock_client)
    mocker.patch("api.topics.get_gemini_api_key", return_value="fake_api_key")

    response = client.post("/api/topics/suggest", json={"query": "environment", "interests": []})

    assert response.status_code == 200
    data = response.json()
    # Check that numbers are cleaned
    assert "Climate Change" in data["suggestions"]
    assert "Renewable Energy" in data["suggestions"]
    assert "Sustainability" in data["suggestions"]
    # Ensure no "1." prefix remains
    assert not any(s.startswith("1.") for s in data["suggestions"])


def test_suggest_topics_with_bullet_points(mocker):
    """Test that bullet points are cleaned up properly"""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "- Economics, - Finance, - Stock Market"
    mock_client.models.generate_content.return_value = mock_response

    mocker.patch("api.topics.genai.Client", return_value=mock_client)
    mocker.patch("api.topics.get_gemini_api_key", return_value="fake_api_key")

    response = client.post("/api/topics/suggest", json={"interests": ["Business"], "query": ""})

    assert response.status_code == 200
    data = response.json()
    # Check that bullet points are cleaned
    assert "Economics" in data["suggestions"]
    assert not any(s.startswith("-") for s in data["suggestions"])


def test_suggest_topics_limits_to_8(mocker):
    """Test that suggestions are limited to max 8 topics"""
    mock_client = MagicMock()
    mock_response = MagicMock()
    # Return more than 8 topics
    mock_response.text = "Topic1, Topic2, Topic3, Topic4, Topic5, Topic6, Topic7, Topic8, Topic9, Topic10"
    mock_client.models.generate_content.return_value = mock_response

    mocker.patch("api.topics.genai.Client", return_value=mock_client)
    mocker.patch("api.topics.get_gemini_api_key", return_value="fake_api_key")

    response = client.post("/api/topics/suggest", json={"query": "test", "interests": []})

    assert response.status_code == 200
    data = response.json()
    # Should be limited to 8
    assert len(data["suggestions"]) == 8


def test_suggest_topics_gemini_error(mocker):
    """Test error handling when Gemini API fails"""
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("API rate limit exceeded")

    mocker.patch("api.topics.genai.Client", return_value=mock_client)
    mocker.patch("api.topics.get_gemini_api_key", return_value="fake_api_key")

    response = client.post("/api/topics/suggest", json={"query": "test", "interests": []})

    assert response.status_code == 500
    assert "Failed to generate topic suggestions" in response.json()["detail"]


def test_suggest_topics_empty_response(mocker):
    """Test handling of empty response from Gemini"""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "   "  # Empty/whitespace response
    mock_client.models.generate_content.return_value = mock_response

    mocker.patch("api.topics.genai.Client", return_value=mock_client)
    mocker.patch("api.topics.get_gemini_api_key", return_value="fake_api_key")

    response = client.post("/api/topics/suggest", json={"query": "test", "interests": []})

    assert response.status_code == 200
    data = response.json()
    # Should return empty list if no valid suggestions
    assert data["suggestions"] == []


def test_suggest_topics_invalid_request():
    """Test validation of request body"""
    # Test with invalid data type for interests
    response = client.post("/api/topics/suggest", json={"interests": "not a list", "query": ""})

    assert response.status_code == 422  # Validation error
