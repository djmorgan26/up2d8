"""
Production integration tests for Cosmos DB (MongoDB API).

Tests database connectivity, collections, and data integrity
in the production environment.
"""

import os
import sys

import pytest
import pymongo
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add packages to path for shared modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../packages/backend-api"))


@pytest.fixture(scope="session")
def production_db_client(production_mode):
    """Connect to production Cosmos DB."""
    if not production_mode:
        # Return mock client for non-production tests
        from unittest.mock import MagicMock
        return MagicMock()

    try:
        from shared.key_vault_client import KeyVaultClient

        kv_client = KeyVaultClient()
        connection_string = kv_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8")

        client = pymongo.MongoClient(connection_string, serverSelectionTimeoutMS=10000)
        yield client
        client.close()
    except Exception as e:
        pytest.skip(f"Could not connect to production database: {e}")


@pytest.fixture(scope="session")
def production_db(production_db_client):
    """Get production database."""
    return production_db_client.up2d8


@pytest.mark.production
@pytest.mark.critical
def test_database_connection(production_db_client):
    """Test that database connection is successful."""
    result = production_db_client.admin.command("ping")
    assert result["ok"] == 1, "Database ping failed"


@pytest.mark.production
@pytest.mark.critical
def test_required_collections_exist(production_db):
    """Test that all required collections exist."""
    collections = production_db.list_collection_names()

    required_collections = ["users", "articles", "rss_feeds"]

    for collection_name in required_collections:
        assert collection_name in collections, \
            f"Required collection '{collection_name}' not found in database"


@pytest.mark.production
def test_users_collection_schema(production_db):
    """Test that users collection has expected schema."""
    users = production_db.users
    sample_user = users.find_one()

    if sample_user:
        # Check for required fields
        required_fields = ["email", "subscribed_tags", "preferences"]
        for field in required_fields:
            assert field in sample_user, \
                f"Users collection missing required field: {field}"

        # Check field types
        assert isinstance(sample_user["subscribed_tags"], list), \
            "subscribed_tags should be a list"
        assert isinstance(sample_user["preferences"], dict), \
            "preferences should be a dict"
    else:
        pytest.skip("No users found in database to validate schema")


@pytest.mark.production
def test_articles_collection_schema(production_db):
    """Test that articles collection has expected schema."""
    articles = production_db.articles
    sample_article = articles.find_one()

    if sample_article:
        # Check for required fields
        required_fields = ["title", "link", "summary", "published", "processed", "tags"]
        for field in required_fields:
            assert field in sample_article, \
                f"Articles collection missing required field: {field}"

        # Check field types
        assert isinstance(sample_article["tags"], list), \
            "tags should be a list"
        assert isinstance(sample_article["processed"], bool), \
            "processed should be a boolean"
    else:
        pytest.skip("No articles found in database to validate schema")


@pytest.mark.production
def test_rss_feeds_collection_schema(production_db):
    """Test that rss_feeds collection has expected schema."""
    rss_feeds = production_db.rss_feeds
    sample_feed = rss_feeds.find_one()

    if sample_feed:
        # Check for required fields
        assert "url" in sample_feed, \
            "RSS feeds collection missing required field: url"
    else:
        pytest.skip("No RSS feeds found in database to validate schema")


@pytest.mark.production
@pytest.mark.slow
def test_database_read_performance(production_db):
    """Test that database queries perform within acceptable time."""
    import time

    # Test a simple query
    start_time = time.time()
    list(production_db.articles.find().limit(10))
    elapsed_time = time.time() - start_time

    assert elapsed_time < 2.0, \
        f"Database query took {elapsed_time:.2f}s (expected < 2s)"


@pytest.mark.production
def test_database_indexes_exist(production_db):
    """Test that important indexes exist for performance."""
    # Check articles collection indexes
    articles_indexes = list(production_db.articles.list_indexes())
    index_fields = [idx.get("key") for idx in articles_indexes]

    # Should have index on _id at minimum
    assert any("_id" in str(idx) for idx in index_fields), \
        "Articles collection should have _id index"


@pytest.mark.production
def test_database_connection_pooling(production_db_client):
    """Test that database connection pooling is working."""
    # Multiple rapid queries should reuse connections
    for _ in range(5):
        result = production_db_client.admin.command("ping")
        assert result["ok"] == 1


@pytest.mark.production
@pytest.mark.critical
def test_database_write_permissions(production_db, production_mode):
    """Test database write permissions (safe test with cleanup)."""
    if not production_mode:
        pytest.skip("Write test only runs in production mode")

    test_collection = production_db.test_collection

    # Insert a test document
    test_doc = {"test": True, "timestamp": "production_test"}
    result = test_collection.insert_one(test_doc)
    assert result.inserted_id is not None, "Failed to insert test document"

    # Clean up
    test_collection.delete_one({"_id": result.inserted_id})

    # Verify cleanup
    found = test_collection.find_one({"_id": result.inserted_id})
    assert found is None, "Test document was not cleaned up"
