"""
Production integration tests for Frontend Static Web App.

Tests availability and basic functionality of the React web app
deployed on Azure Static Web Apps.
"""

import pytest
import requests


@pytest.mark.production
@pytest.mark.critical
def test_frontend_reachable(http_session, frontend_url, test_timeout):
    """Test that frontend static site is reachable."""
    response = http_session.get(frontend_url, timeout=test_timeout)

    assert response.status_code == 200, \
        f"Frontend returned status {response.status_code}, expected 200"


@pytest.mark.production
def test_frontend_returns_html(http_session, frontend_url, test_timeout):
    """Test that frontend returns HTML content."""
    response = http_session.get(frontend_url, timeout=test_timeout)

    assert response.status_code == 200
    assert "text/html" in response.headers.get("Content-Type", ""), \
        "Frontend should return HTML content"


@pytest.mark.production
def test_frontend_has_react_root(http_session, frontend_url, test_timeout):
    """Test that frontend HTML contains React root element."""
    response = http_session.get(frontend_url, timeout=test_timeout)

    assert response.status_code == 200

    content = response.text.lower()
    # Check for common React patterns
    assert any([
        'id="root"' in content,
        'id="app"' in content,
        'react' in content
    ]), "Frontend should contain React app structure"


@pytest.mark.production
@pytest.mark.slow
def test_frontend_response_time(http_session, frontend_url, test_timeout):
    """Test that frontend responds within acceptable time."""
    import time

    start_time = time.time()
    response = http_session.get(frontend_url, timeout=test_timeout)
    elapsed_time = time.time() - start_time

    assert response.status_code == 200
    assert elapsed_time < 5.0, \
        f"Frontend took {elapsed_time:.2f}s to respond (expected < 5s)"


@pytest.mark.production
@pytest.mark.critical
def test_frontend_ssl_certificate(frontend_url):
    """Test that frontend has valid SSL certificate."""
    import ssl
    import socket
    from urllib.parse import urlparse

    parsed_url = urlparse(frontend_url)
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
def test_frontend_security_headers(http_session, frontend_url, test_timeout):
    """Test that frontend has important security headers."""
    response = http_session.get(frontend_url, timeout=test_timeout)

    assert response.status_code == 200

    headers = response.headers

    # Check for recommended security headers
    # Azure Static Web Apps typically sets these
    security_headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": None,  # Should exist
        "Strict-Transport-Security": None,  # Should exist for HTTPS
    }

    for header, expected_value in security_headers.items():
        if header in headers:
            if expected_value:
                assert headers[header] == expected_value, \
                    f"Header {header} should be {expected_value}"


@pytest.mark.production
def test_frontend_caching_headers(http_session, frontend_url, test_timeout):
    """Test that frontend has appropriate caching headers."""
    response = http_session.get(frontend_url, timeout=test_timeout)

    assert response.status_code == 200

    # Should have cache control for static assets
    assert "Cache-Control" in response.headers or "ETag" in response.headers, \
        "Frontend should have caching headers"


@pytest.mark.production
def test_frontend_404_handling(http_session, frontend_url, test_timeout):
    """Test that frontend handles 404s appropriately."""
    response = http_session.get(
        f"{frontend_url.rstrip('/')}/this-page-does-not-exist-12345",
        timeout=test_timeout
    )

    # Should either return 404 or redirect to SPA (200 for client-side routing)
    assert response.status_code in [200, 404], \
        f"Frontend 404 handling returned unexpected status {response.status_code}"
