"""
Production test configuration and fixtures.

This module provides pytest fixtures for testing production Azure services.
Tests can be run in two modes:
  - PROD_TEST_MODE=live: Tests against actual Azure production services
  - PROD_TEST_MODE=mock: Uses mocked responses (default)
"""

import os
import sys
from typing import Generator
from unittest.mock import MagicMock

import pytest
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add packages to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../packages/backend-api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../packages/functions"))


@pytest.fixture(scope="session")
def production_mode() -> bool:
    """Determine if tests should run against production or use mocks."""
    mode = os.getenv("PROD_TEST_MODE", "mock").lower()
    return mode == "live"


@pytest.fixture(scope="session")
def backend_api_url() -> str:
    """Backend API production URL."""
    url = os.getenv("AZURE-BACKEND-APP-URL", "up2d8.azurewebsites.net")
    if not url.startswith("http"):
        url = f"https://{url}"
    return url


@pytest.fixture(scope="session")
def function_app_url() -> str:
    """Azure Function App production URL."""
    return os.getenv("AZURE-FUNCTION-APP-URL", "https://up2d8-function-app.azurewebsites.net/")


@pytest.fixture(scope="session")
def frontend_url() -> str:
    """Frontend static site production URL."""
    return os.getenv("AZURE-FRONTEND-APP-URL", "https://gray-wave-00bdfc60f.3.azurestaticapps.net")


@pytest.fixture
def http_session(production_mode) -> Generator[requests.Session, None, None]:
    """Provides HTTP session for making requests to production services."""
    if not production_mode:
        # Return a mocked session when not in production mode
        mock_session = MagicMock(spec=requests.Session)
        yield mock_session
    else:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "UP2D8-Production-Tests/1.0",
            "Accept": "application/json"
        })
        yield session
        session.close()


@pytest.fixture
def test_timeout() -> int:
    """Timeout for production test requests (in seconds)."""
    return int(os.getenv("PROD_TEST_TIMEOUT", "30"))


@pytest.fixture(scope="session")
def azure_credentials():
    """Azure credentials for authenticated tests."""
    return {
        "subscription_id": os.getenv("AZURE-SUBSCRIPTION-ID"),
        "resource_group": os.getenv("AZURE-RESOURCE-GROUP-NAME", "personal-rg"),
        "tenant_id": os.getenv("ENTRA_TENANT_ID"),
        "client_id": os.getenv("ENTRA_CLIENT_ID"),
    }


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "production: mark test as production integration test (requires PROD_TEST_MODE=live)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "critical: mark test as critical for service health"
    )


def pytest_collection_modifyitems(config, items):
    """Skip production tests if not in production mode."""
    production_mode = os.getenv("PROD_TEST_MODE", "mock").lower() == "live"

    if not production_mode:
        skip_production = pytest.mark.skip(reason="Production tests require PROD_TEST_MODE=live")
        for item in items:
            if "production" in item.keywords:
                item.add_marker(skip_production)
