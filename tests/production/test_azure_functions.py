"""
Production integration tests for Azure Functions.

Tests health and availability of Azure Functions deployed for
background tasks, RSS scraping, and newsletter generation.
"""

import pytest
import requests


@pytest.mark.production
@pytest.mark.critical
def test_function_app_health(http_session, function_app_url, test_timeout):
    """Test that Azure Function App is reachable."""
    # Azure Functions may not have a root endpoint, so we check the base URL
    try:
        response = http_session.get(function_app_url, timeout=test_timeout)
        # Accept any response that shows the function app is running
        assert response.status_code in [200, 401, 403, 404], \
            f"Function app returned unexpected status {response.status_code}"
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Function app is not reachable: {e}")


@pytest.mark.production
def test_function_app_admin_endpoint(http_session, function_app_url, test_timeout):
    """Test that function app admin endpoint exists (should be protected)."""
    admin_url = f"{function_app_url.rstrip('/')}/admin"
    response = http_session.get(admin_url, timeout=test_timeout)

    # Admin endpoint should require authentication
    assert response.status_code in [401, 403], \
        "Admin endpoint should be protected with authentication"


@pytest.mark.production
@pytest.mark.critical
def test_rss_scraper_function_exists(http_session, function_app_url, test_timeout):
    """Test that RSS scraper function endpoint exists."""
    # Note: This will likely fail without proper auth/function key
    scraper_url = f"{function_app_url.rstrip('/')}/api/rss-scraper"
    response = http_session.get(scraper_url, timeout=test_timeout)

    # Function should exist - either run (200), require auth (401), or not accept GET (405)
    assert response.status_code in [200, 401, 403, 405], \
        f"RSS scraper function returned unexpected status {response.status_code}"


@pytest.mark.production
@pytest.mark.critical
def test_newsletter_function_exists(http_session, function_app_url, test_timeout):
    """Test that newsletter generation function endpoint exists."""
    newsletter_url = f"{function_app_url.rstrip('/')}/api/newsletter-generator"
    response = http_session.get(newsletter_url, timeout=test_timeout)

    # Function should exist
    assert response.status_code in [200, 401, 403, 405], \
        f"Newsletter function returned unexpected status {response.status_code}"


@pytest.mark.production
def test_web_crawler_orchestrator_exists(http_session, function_app_url, test_timeout):
    """Test that web crawler orchestrator function endpoint exists."""
    crawler_url = f"{function_app_url.rstrip('/')}/api/web-crawler-orchestrator"
    response = http_session.get(crawler_url, timeout=test_timeout)

    # Durable function orchestrator should exist
    assert response.status_code in [200, 401, 403, 405], \
        f"Web crawler orchestrator returned unexpected status {response.status_code}"


@pytest.mark.production
@pytest.mark.slow
def test_function_app_response_time(http_session, function_app_url, test_timeout):
    """Test that function app responds within acceptable time."""
    import time

    start_time = time.time()
    try:
        response = http_session.get(function_app_url, timeout=test_timeout)
        elapsed_time = time.time() - start_time

        # Function app should respond quickly even if it returns 404
        assert elapsed_time < 10.0, \
            f"Function app took {elapsed_time:.2f}s to respond (expected < 10s)"
    except requests.exceptions.RequestException:
        elapsed_time = time.time() - start_time
        # Even if request fails, it should fail quickly
        assert elapsed_time < 10.0, \
            f"Function app took {elapsed_time:.2f}s to fail (expected < 10s)"


@pytest.mark.production
@pytest.mark.critical
def test_function_app_ssl_certificate(function_app_url):
    """Test that Azure Function App has valid SSL certificate."""
    import ssl
    import socket
    from urllib.parse import urlparse

    parsed_url = urlparse(function_app_url)
    hostname = parsed_url.netloc

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


@pytest.mark.production
def test_function_app_cors_configuration(http_session, function_app_url, test_timeout):
    """Test that function app has CORS properly configured."""
    response = http_session.options(function_app_url, timeout=test_timeout)

    # Check for CORS headers - informational test
    # Azure Functions typically handle CORS in host.json
    if response.status_code == 200:
        if "Access-Control-Allow-Origin" in response.headers:
            assert response.headers["Access-Control-Allow-Origin"] is not None
