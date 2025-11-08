import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app
import pymongo
import os

@pytest.fixture(scope="session")
def real_mongo_db():
    # Use a test-specific database name to avoid interfering with the main application
    test_db_name = "up2d8_test_db"
    
    # Get MongoDB connection string from environment variable or use a default for local testing
    from dotenv import load_dotenv
    from shared.key_vault_client import KeyVaultClient

    load_dotenv()
    kv_client = KeyVaultClient()
    mongo_connection_string = os.getenv("TEST_MONGO_DB_CONNECTION_STRING", kv_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8"))
    
    client = pymongo.MongoClient(mongo_connection_string)
    db = client[test_db_name]

    # Clear the database before tests run
    for collection_name in db.list_collection_names():
        db.drop_collection(collection_name)

    yield db

    # Clear the database after tests run
    for collection_name in db.list_collection_names():
        db.drop_collection(collection_name)

from dependencies import get_db_client # Import the dependency to override
from unittest.mock import MagicMock

@pytest.fixture(scope="module")
def test_client():
    mock_db_client = MagicMock()
    app.dependency_overrides[get_db_client] = lambda: mock_db_client
    with TestClient(app) as client:
        yield client, mock_db_client # Yield both client and mock_db_client
    app.dependency_overrides = {} # Clear overrides after tests
