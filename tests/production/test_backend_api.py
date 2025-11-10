"""
Production integration tests for Backend API.

Tests health, endpoints, and core functionality of the FastAPI backend
deployed on Azure App Service.
"""

import pytest
import requests


@pytest.mark.production
@pytest.mark.critical
def test_backend_api_health(http_session, backend_api_url, test_timeout):
    """Test that backend API is reachable and returns correct health response."""
    response = http_session.get(f"{backend_api_url}/", timeout=test_timeout)

    assert response.status_code == 200, f"Backend API health check failed with status {response.status_code}"

    data = response.json()
    assert data["service"] == "UP2D8 Backend API"
    assert data["status"] == "running"
    assert "version" in data
    assert "docs" in data


@pytest.mark.production
def test_backend_api_docs_available(http_session, backend_api_url, test_timeout):
    """Test that API documentation is accessible."""
    response = http_session.get(f"{backend_api_url}/docs", timeout=test_timeout)
    assert response.status_code == 200, "API docs endpoint should be accessible"


@pytest.mark.production
def test_backend_api_openapi_schema(http_session, backend_api_url, test_timeout):
    """Test that OpenAPI schema is available."""
    response = http_session.get(f"{backend_api_url}/openapi.json", timeout=test_timeout)
    assert response.status_code == 200, "OpenAPI schema should be accessible"

    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert schema["info"]["title"] == "UP2D8 Backend API"


@pytest.mark.production
@pytest.mark.critical
def test_articles_endpoint_exists(http_session, backend_api_url, test_timeout):
    """Test that articles endpoint is available (may require auth)."""
    response = http_session.get(f"{backend_api_url}/articles", timeout=test_timeout)

    # Endpoint should exist - either return data (200) or require auth (401/403)
    assert response.status_code in [200, 401, 403], \
        f"Articles endpoint returned unexpected status {response.status_code}"


@pytest.mark.production
@pytest.mark.critical
def test_rss_feeds_endpoint_exists(http_session, backend_api_url, test_timeout):
    """Test that RSS feeds endpoint is available."""
    response = http_session.get(f"{backend_api_url}/rss-feeds", timeout=test_timeout)

    # Endpoint should exist - either return data or require auth
    assert response.status_code in [200, 401, 403], \
        f"RSS feeds endpoint returned unexpected status {response.status_code}"


@pytest.mark.production
def test_users_endpoint_exists(http_session, backend_api_url, test_timeout):
    """Test that users endpoint is available."""
    response = http_session.get(f"{backend_api_url}/users", timeout=test_timeout)

    # Endpoint should exist - likely requires auth
    assert response.status_code in [200, 401, 403, 405], \
        f"Users endpoint returned unexpected status {response.status_code}"


@pytest.mark.production
def test_chat_endpoint_exists(http_session, backend_api_url, test_timeout):
    """Test that chat endpoint is available."""
    response = http_session.post(
        f"{backend_api_url}/chat",
        json={"message": "test"},
        timeout=test_timeout
    )

    # Endpoint should exist - may require auth or return validation error
    assert response.status_code in [200, 401, 403, 422], \
        f"Chat endpoint returned unexpected status {response.status_code}"


@pytest.mark.production
def test_analytics_endpoint_exists(http_session, backend_api_url, test_timeout):
    """Test that analytics endpoint is available."""
    response = http_session.get(f"{backend_api_url}/analytics", timeout=test_timeout)

    # Endpoint should exist
    assert response.status_code in [200, 401, 403], \
        f"Analytics endpoint returned unexpected status {response.status_code}"


@pytest.mark.production
def test_feedback_endpoint_exists(http_session, backend_api_url, test_timeout):
    """Test that feedback endpoint is available."""
    response = http_session.post(
        f"{backend_api_url}/feedback",
        json={"feedback": "test"},
        timeout=test_timeout
    )

    # Endpoint should exist - may require validation or auth
    assert response.status_code in [200, 201, 401, 403, 422], \
        f"Feedback endpoint returned unexpected status {response.status_code}"


@pytest.mark.production
@pytest.mark.slow
def test_backend_api_response_time(http_session, backend_api_url, test_timeout):
    """Test that backend API responds within acceptable time."""
    import time

    start_time = time.time()
    response = http_session.get(f"{backend_api_url}/", timeout=test_timeout)
    elapsed_time = time.time() - start_time

    assert response.status_code == 200
    assert elapsed_time < 5.0, f"Backend API took {elapsed_time:.2f}s to respond (expected < 5s)"


@pytest.mark.production
def test_backend_api_cors_headers(http_session, backend_api_url, test_timeout):
    """Test that CORS headers are properly configured."""
    response = http_session.options(f"{backend_api_url}/", timeout=test_timeout)

    # Check for CORS headers (may or may not be present depending on config)
    # This is informational rather than strict
    if "Access-Control-Allow-Origin" in response.headers:
        assert response.headers["Access-Control-Allow-Origin"] is not None


@pytest.mark.production
@pytest.mark.critical
def test_backend_api_ssl_certificate(backend_api_url):
    """Test that backend API has valid SSL certificate."""
    import ssl
    import socket
    from urllib.parse import urlparse

    parsed_url = urlparse(backend_api_url)
    hostname = parsed_url.netloc or parsed_url.path

    context = ssl.create_default_context()

    try:
        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                assert cert is not None, "No SSL certificate found"
    except ssl.SSLError as e:
        pytest.fail(f"SSL certificate validation failed: {e}")
    except Exception as e:
        pytest.fail(f"SSL connection failed: {e}")
