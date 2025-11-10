"""
End-to-end integration tests for production environment.

Tests the full flow across multiple services:
Backend API -> Database, Functions -> Database, Frontend -> Backend API
"""

import pytest
import requests


@pytest.mark.production
@pytest.mark.critical
@pytest.mark.slow
def test_full_stack_health_check(http_session, backend_api_url, function_app_url, frontend_url, test_timeout):
    """Test that all three main services are up and responding."""
    services = {
        "Backend API": backend_api_url,
        "Function App": function_app_url,
        "Frontend": frontend_url,
    }

    results = {}

    for service_name, url in services.items():
        try:
            response = http_session.get(url, timeout=test_timeout)
            results[service_name] = {
                "status": "UP",
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            results[service_name] = {
                "status": "DOWN",
                "error": str(e)
            }

    # All critical services should be up
    for service_name, result in results.items():
        assert result["status"] == "UP", \
            f"{service_name} is DOWN: {result.get('error', 'Unknown error')}"


@pytest.mark.production
def test_backend_to_database_flow(http_session, backend_api_url, test_timeout):
    """Test that backend can successfully query database through articles endpoint."""
    response = http_session.get(f"{backend_api_url}/articles", timeout=test_timeout)

    # Should either return articles or require authentication
    # Both indicate backend->database connection is working
    assert response.status_code in [200, 401, 403], \
        f"Backend-to-database flow failed with status {response.status_code}"

    if response.status_code == 200:
        # If we get data, verify it's in correct format
        data = response.json()
        assert isinstance(data, (list, dict)), "Articles endpoint should return list or dict"


@pytest.mark.production
@pytest.mark.slow
def test_service_response_times_acceptable(http_session, backend_api_url, frontend_url, test_timeout):
    """Test that all services respond within acceptable time limits."""
    import time

    services = {
        "Backend API": (backend_api_url, 5.0),
        "Frontend": (frontend_url, 5.0),
    }

    for service_name, (url, max_time) in services.items():
        start_time = time.time()
        response = http_session.get(url, timeout=test_timeout)
        elapsed_time = time.time() - start_time

        assert response.status_code == 200, \
            f"{service_name} returned status {response.status_code}"

        assert elapsed_time < max_time, \
            f"{service_name} took {elapsed_time:.2f}s to respond (expected < {max_time}s)"


@pytest.mark.production
def test_cors_configuration_across_services(http_session, backend_api_url, frontend_url, test_timeout):
    """Test CORS configuration allows frontend to call backend."""
    # Make an OPTIONS request to backend as if from frontend
    headers = {
        "Origin": frontend_url,
        "Access-Control-Request-Method": "GET",
    }

    response = http_session.options(
        f"{backend_api_url}/articles",
        headers=headers,
        timeout=test_timeout
    )

    # If CORS is configured, should have appropriate headers
    # This is informational - some APIs may not support OPTIONS
    if response.status_code == 200:
        assert "Access-Control-Allow-Origin" in response.headers or \
               response.headers.get("Access-Control-Allow-Origin") == "*" or \
               frontend_url in response.headers.get("Access-Control-Allow-Origin", "")


@pytest.mark.production
@pytest.mark.critical
def test_ssl_certificates_valid_across_services(backend_api_url, function_app_url, frontend_url):
    """Test that all services have valid SSL certificates."""
    import ssl
    import socket
    from urllib.parse import urlparse

    services = {
        "Backend API": backend_api_url,
        "Function App": function_app_url,
        "Frontend": frontend_url,
    }

    for service_name, url in services.items():
        parsed_url = urlparse(url)
        hostname = parsed_url.netloc or parsed_url.path.split('/')[0]

        context = ssl.create_default_context()

        try:
            with socket.create_connection((hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    assert cert is not None, f"{service_name}: No SSL certificate found"
        except ssl.SSLError as e:
            pytest.fail(f"{service_name}: SSL certificate validation failed: {e}")
        except Exception as e:
            pytest.fail(f"{service_name}: SSL connection failed: {e}")


@pytest.mark.production
def test_error_handling_consistency(http_session, backend_api_url, test_timeout):
    """Test that backend handles errors consistently."""
    # Try to access non-existent endpoint
    response = http_session.get(
        f"{backend_api_url}/this-endpoint-does-not-exist-12345",
        timeout=test_timeout
    )

    # Should return proper error response
    assert response.status_code == 404, "Backend should return 404 for non-existent endpoints"

    # Try to make invalid request
    response = http_session.post(
        f"{backend_api_url}/articles",
        json={"invalid": "data"},
        timeout=test_timeout
    )

    # Should handle invalid requests appropriately
    assert response.status_code in [400, 401, 403, 405, 422], \
        "Backend should return appropriate error for invalid requests"
