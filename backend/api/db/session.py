"""Database session management and connection for MongoDB.

Provides MongoDB client and database access using pymongo.
Works with both local MongoDB and Azure Cosmos DB MongoDB API.
"""

import os
from typing import Generator, Optional
from pymongo import MongoClient
from pymongo.database import Database
import structlog

logger = structlog.get_logger()

# MongoDB URL from environment variable
MONGODB_URL = os.getenv("MONGODB_URL") or os.getenv("COSMOS_DB_CONNECTION_STRING")
DB_NAME = os.getenv("COSMOS_DB_NAME", "up2d8")

if not MONGODB_URL:
    raise ValueError(
        "MONGODB_URL or COSMOS_DB_CONNECTION_STRING environment variable is not set. "
        "Please set it in your .env file or environment."
    )

# Global MongoDB client instance
_mongo_client: Optional[MongoClient] = None
_database: Optional[Database] = None


def get_mongo_client() -> MongoClient:
    """
    Get or create MongoDB client singleton.

    Returns:
        MongoClient instance
    """
    global _mongo_client

    if _mongo_client is None:
        _mongo_client = MongoClient(
            MONGODB_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
        )
        logger.info("mongodb_client_initialized", database=DB_NAME)

    return _mongo_client


def get_database() -> Database:
    """
    Get MongoDB database instance.

    Returns:
        Database instance
    """
    global _database

    if _database is None:
        client = get_mongo_client()
        _database = client[DB_NAME]

    return _database


def get_db() -> Generator[Database, None, None]:
    """
    Dependency function for FastAPI to get database sessions.

    Usage:
        @app.get("/users")
        def get_users(db: Database = Depends(get_db)):
            users_collection = db["users"]
            ...

    Yields:
        Database instance
    """
    db = get_database()
    try:
        yield db
    finally:
        # MongoDB connections are managed by the connection pool
        # No need to explicitly close per-request
        pass


def close_db_connection():
    """Close MongoDB connection."""
    global _mongo_client, _database

    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
        _database = None
        logger.info("mongodb_connection_closed")


def init_db() -> None:
    """Initialize database - create indexes."""
    from api.db.cosmos_db import create_indexes

    logger.info("initializing_database")
    create_indexes()
    logger.info("database_initialized")


def drop_db() -> None:
    """Drop all database collections. WARNING: Use with caution!"""
    db = get_database()

    logger.warning("dropping_all_collections")

    for collection_name in db.list_collection_names():
        db.drop_collection(collection_name)

    logger.warning("all_collections_dropped")
