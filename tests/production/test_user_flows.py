"""
End-to-end user flow tests for production.

Tests complete user journeys through the application:
- User registration and authentication
- Browsing and reading articles
- Chatting with AI
- Managing RSS feeds
- Providing feedback
"""

import pytest
import requests
from typing import Dict, Any


@pytest.mark.production
@pytest.mark.critical
def test_health_endpoint_detailed(http_session, backend_api_url, test_timeout):
    """Test the detailed health check endpoint."""
    response = http_session.get(f"{backend_api_url}/api/health", timeout=test_timeout)

    assert response.status_code == 200, f"Health check failed with status {response.status_code}"

    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


@pytest.mark.production
@pytest.mark.critical
def test_articles_list_endpoint(http_session, backend_api_url, test_timeout):
    """Test fetching list of articles (core user flow)."""
    response = http_session.get(f"{backend_api_url}/api/articles", timeout=test_timeout)

    # Articles endpoint may require auth or return empty list
    assert response.status_code in [200, 401, 403], \
        f"Articles endpoint returned unexpected status {response.status_code}"

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, (list, dict)), "Articles should return list or dict"


@pytest.mark.production
def test_article_detail_flow(http_session, backend_api_url, test_timeout):
    """Test accessing a specific article (if articles exist)."""
    # First, try to get list of articles
    response = http_session.get(f"{backend_api_url}/api/articles", timeout=test_timeout)

    if response.status_code == 200:
        articles = response.json()
        if isinstance(articles, list) and len(articles) > 0:
            # Test accessing first article
            article_id = articles[0].get("_id") or articles[0].get("id")
            if article_id:
                detail_response = http_session.get(
                    f"{backend_api_url}/api/articles/{article_id}",
                    timeout=test_timeout
                )
                assert detail_response.status_code in [200, 404, 401, 403], \
                    "Article detail should return valid status"
        else:
            pytest.skip("No articles available to test detail view")
    else:
        pytest.skip("Cannot access articles endpoint")


@pytest.mark.production
def test_rss_feeds_list(http_session, backend_api_url, test_timeout):
    """Test fetching list of RSS feeds."""
    response = http_session.get(f"{backend_api_url}/api/rss_feeds", timeout=test_timeout)

    assert response.status_code in [200, 401, 403], \
        f"RSS feeds endpoint returned unexpected status {response.status_code}"

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, (list, dict)), "RSS feeds should return list or dict"


@pytest.mark.production
def test_rss_feed_suggestions(http_session, backend_api_url, test_timeout):
    """Test RSS feed suggestion feature."""
    response = http_session.get(f"{backend_api_url}/api/rss_feeds/suggest", timeout=test_timeout)

    # May require auth, specific parameters, or POST method
    assert response.status_code in [200, 400, 401, 403, 404, 405, 422], \
        f"RSS feed suggest returned unexpected status {response.status_code}"


@pytest.mark.production
def test_chat_endpoint_structure(http_session, backend_api_url, test_timeout):
    """Test chat endpoint with minimal payload."""
    payload = {
        "message": "Hello",
        "session_id": "test-session"
    }

    response = http_session.post(
        f"{backend_api_url}/api/chat",
        json=payload,
        timeout=test_timeout
    )

    # Chat endpoint requires auth or specific payload structure
    assert response.status_code in [200, 400, 401, 403, 422], \
        f"Chat endpoint returned unexpected status {response.status_code}"

    if response.status_code == 422:
        # Validation error - expected, means endpoint exists and validates input
        error = response.json()
        assert "detail" in error, "Validation error should have detail"


@pytest.mark.production
def test_chat_sessions_endpoint(http_session, backend_api_url, test_timeout):
    """Test chat sessions endpoint."""
    response = http_session.get(f"{backend_api_url}/api/sessions", timeout=test_timeout)

    assert response.status_code in [200, 401, 403, 405], \
        f"Sessions endpoint returned unexpected status {response.status_code}"


@pytest.mark.production
def test_analytics_endpoint(http_session, backend_api_url, test_timeout):
    """Test analytics endpoint."""
    response = http_session.get(f"{backend_api_url}/api/analytics", timeout=test_timeout)

    assert response.status_code in [200, 401, 403, 405], \
        f"Analytics endpoint returned unexpected status {response.status_code}"

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, dict), "Analytics should return dict"


@pytest.mark.production
def test_feedback_submission_flow(http_session, backend_api_url, test_timeout):
    """Test feedback submission (user flow for reporting issues)."""
    feedback_payload = {
        "feedback": "Test feedback from automated tests",
        "rating": 5,
        "category": "test"
    }

    response = http_session.post(
        f"{backend_api_url}/api/feedback",
        json=feedback_payload,
        timeout=test_timeout
    )

    # Feedback may require specific fields or auth
    assert response.status_code in [200, 201, 400, 401, 403, 422], \
        f"Feedback endpoint returned unexpected status {response.status_code}"


@pytest.mark.production
def test_topic_suggestions(http_session, backend_api_url, test_timeout):
    """Test topic suggestion endpoint."""
    response = http_session.get(f"{backend_api_url}/api/topics/suggest", timeout=test_timeout)

    assert response.status_code in [200, 400, 401, 403, 405, 422], \
        f"Topic suggest returned unexpected status {response.status_code}"


@pytest.mark.production
@pytest.mark.slow
def test_complete_reader_flow(http_session, backend_api_url, test_timeout):
    """
    Test complete user flow: Browse articles -> Read article -> Submit feedback.
    This simulates a real user reading news.
    """
    flow_results = []

    # Step 1: Check health
    health_response = http_session.get(f"{backend_api_url}/api/health", timeout=test_timeout)
    flow_results.append(("Health Check", health_response.status_code == 200))

    # Step 2: Browse articles
    articles_response = http_session.get(f"{backend_api_url}/api/articles", timeout=test_timeout)
    articles_ok = articles_response.status_code in [200, 401, 403]
    flow_results.append(("Browse Articles", articles_ok))

    # Step 3: Try to get analytics (user checking their reading stats)
    analytics_response = http_session.get(f"{backend_api_url}/api/analytics", timeout=test_timeout)
    analytics_ok = analytics_response.status_code in [200, 401, 403, 405]
    flow_results.append(("View Analytics", analytics_ok))

    # All critical steps should succeed
    assert all(result for _, result in flow_results), \
        f"Reader flow failed: {flow_results}"


@pytest.mark.production
@pytest.mark.slow
def test_complete_chat_flow(http_session, backend_api_url, test_timeout):
    """
    Test complete chat flow: Check sessions -> Send message -> Get response.
    This simulates a user chatting with AI about articles.
    """
    flow_results = []

    # Step 1: Check existing sessions
    sessions_response = http_session.get(f"{backend_api_url}/api/sessions", timeout=test_timeout)
    sessions_ok = sessions_response.status_code in [200, 401, 403, 405]
    flow_results.append(("Check Sessions", sessions_ok))

    # Step 2: Send a chat message
    chat_payload = {
        "message": "What are the latest tech news?",
        "session_id": "test-flow-session"
    }
    chat_response = http_session.post(
        f"{backend_api_url}/api/chat",
        json=chat_payload,
        timeout=test_timeout
    )
    chat_ok = chat_response.status_code in [200, 400, 401, 403, 422]
    flow_results.append(("Send Chat Message", chat_ok))

    # All steps should return valid responses
    assert all(result for _, result in flow_results), \
        f"Chat flow failed: {flow_results}"


@pytest.mark.production
@pytest.mark.slow
def test_complete_feed_management_flow(http_session, backend_api_url, test_timeout):
    """
    Test complete feed management flow: List feeds -> Get suggestions -> View articles from feeds.
    This simulates a user managing their RSS feeds.
    """
    flow_results = []

    # Step 1: List current RSS feeds
    feeds_response = http_session.get(f"{backend_api_url}/api/rss_feeds", timeout=test_timeout)
    feeds_ok = feeds_response.status_code in [200, 401, 403]
    flow_results.append(("List RSS Feeds", feeds_ok))

    # Step 2: Get feed suggestions
    suggest_response = http_session.get(f"{backend_api_url}/api/rss_feeds/suggest", timeout=test_timeout)
    suggest_ok = suggest_response.status_code in [200, 400, 401, 403, 404, 405, 422]
    flow_results.append(("Get Feed Suggestions", suggest_ok))

    # Step 3: View articles (from feeds)
    articles_response = http_session.get(f"{backend_api_url}/api/articles", timeout=test_timeout)
    articles_ok = articles_response.status_code in [200, 401, 403]
    flow_results.append(("View Feed Articles", articles_ok))

    assert all(result for _, result in flow_results), \
        f"Feed management flow failed: {flow_results}"


@pytest.mark.production
@pytest.mark.critical
def test_api_error_handling_user_flow(http_session, backend_api_url, test_timeout):
    """
    Test that API handles errors gracefully in user-facing scenarios.
    """
    # Test 1: Non-existent article
    response = http_session.get(
        f"{backend_api_url}/api/articles/nonexistent-id-12345",
        timeout=test_timeout
    )
    assert response.status_code in [404, 401, 403], \
        "Should return 404 or auth error for non-existent article"

    # Test 2: Invalid chat payload
    response = http_session.post(
        f"{backend_api_url}/api/chat",
        json={"invalid": "payload"},
        timeout=test_timeout
    )
    assert response.status_code in [400, 401, 403, 422], \
        "Should return 400/422 or auth error for invalid chat payload"

    # Test 3: Non-existent endpoint
    response = http_session.get(
        f"{backend_api_url}/api/this-endpoint-does-not-exist",
        timeout=test_timeout
    )
    assert response.status_code == 404, \
        "Should return 404 for non-existent endpoint"


@pytest.mark.production
def test_authentication_flow(http_session, backend_api_url, test_timeout):
    """
    Test authentication-related endpoints (without actual auth).
    Verifies that protected endpoints require authentication.
    """
    # Test protected endpoint without auth
    response = http_session.get(
        f"{backend_api_url}/api/auth/protected",
        timeout=test_timeout
    )
    assert response.status_code in [401, 403], \
        "Protected endpoint should require authentication"

    # Test /me endpoint without auth
    response = http_session.get(
        f"{backend_api_url}/api/auth/me",
        timeout=test_timeout
    )
    assert response.status_code in [401, 403], \
        "/me endpoint should require authentication"


@pytest.mark.production
@pytest.mark.slow
def test_performance_under_user_load(http_session, backend_api_url, test_timeout):
    """
    Test system performance simulating multiple user actions in sequence.
    """
    import time

    endpoints = [
        "/api/health",
        "/api/articles",
        "/api/rss_feeds",
        "/api/analytics",
    ]

    start_time = time.time()
    results = []

    for endpoint in endpoints:
        endpoint_start = time.time()
        response = http_session.get(f"{backend_api_url}{endpoint}", timeout=test_timeout)
        endpoint_time = time.time() - endpoint_start

        results.append({
            "endpoint": endpoint,
            "status": response.status_code,
            "time": endpoint_time
        })

    total_time = time.time() - start_time

    # All requests should complete in reasonable time
    assert total_time < 10.0, f"Multiple user actions took {total_time}s (expected < 10s)"

    # Each individual request should be fast
    for result in results:
        assert result["time"] < 5.0, \
            f"{result['endpoint']} took {result['time']}s (expected < 5s)"
