"""
Azure Cosmos DB Client
MongoDB API implementation for Azure Cosmos DB
"""
import os
from typing import Optional, Dict, List, Any
from datetime import datetime
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
import structlog

logger = structlog.get_logger()


class CosmosDBClient:
    """
    Azure Cosmos DB client using MongoDB API

    Provides a simple abstraction over MongoDB API for Cosmos DB.
    Compatible with the existing database models.
    """

    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize Cosmos DB client

        Args:
            connection_string: MongoDB connection string for Cosmos DB
        """
        self.connection_string = connection_string or os.getenv("COSMOS_DB_CONNECTION_STRING")

        if not self.connection_string:
            raise ValueError("COSMOS_DB_CONNECTION_STRING environment variable must be set")

        # Initialize MongoDB client
        self.client: MongoClient = MongoClient(
            self.connection_string,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
        )

        # Get database (default: up2d8)
        self.db_name = os.getenv("COSMOS_DB_NAME", "up2d8")
        self.db: Database = self.client[self.db_name]

        logger.info("cosmos_db_initialized", database=self.db_name)

    def get_collection(self, collection_name: str) -> Collection:
        """Get a collection from the database"""
        return self.db[collection_name]

    def close(self):
        """Close the database connection"""
        self.client.close()
        logger.info("cosmos_db_closed")


# Singleton instance
_cosmos_client: Optional[CosmosDBClient] = None


def get_cosmos_client() -> CosmosDBClient:
    """
    Get or create the Cosmos DB client singleton

    Returns:
        CosmosDBClient instance
    """
    global _cosmos_client

    if _cosmos_client is None:
        _cosmos_client = CosmosDBClient()

    return _cosmos_client


def close_cosmos_client():
    """Close the Cosmos DB client"""
    global _cosmos_client

    if _cosmos_client is not None:
        _cosmos_client.close()
        _cosmos_client = None


# Collection helpers
class CosmosCollections:
    """Collection name constants"""
    USERS = "users"
    USER_PREFERENCES = "user_preferences"
    ARTICLES = "articles"
    DIGESTS = "digests"
    CHAT_SESSIONS = "chat_sessions"
    CHAT_MESSAGES = "chat_messages"
    FEEDBACK = "feedback"
    ANALYTICS = "analytics"


def create_indexes():
    """
    Create database indexes for better query performance

    This should be run once during initial setup or deployment
    """
    client = get_cosmos_client()

    # Users collection
    users = client.get_collection(CosmosCollections.USERS)
    users.create_index("email", unique=True)
    users.create_index("created_at")
    users.create_index([("status", 1), ("tier", 1)])

    # Articles collection
    articles = client.get_collection(CosmosCollections.ARTICLES)
    articles.create_index("url", unique=True)
    articles.create_index([("source_id", 1), ("created_at", -1)])
    articles.create_index([("processing_status", 1), ("created_at", -1)])
    articles.create_index("published_at")

    # Digests collection
    digests = client.get_collection(CosmosCollections.DIGESTS)
    digests.create_index([("user_id", 1), ("created_at", -1)])
    digests.create_index([("status", 1), ("created_at", -1)])

    # Chat sessions collection
    chat_sessions = client.get_collection(CosmosCollections.CHAT_SESSIONS)
    chat_sessions.create_index([("user_id", 1), ("created_at", -1)])

    # Chat messages collection
    chat_messages = client.get_collection(CosmosCollections.CHAT_MESSAGES)
    chat_messages.create_index([("session_id", 1), ("created_at", 1)])

    logger.info("cosmos_db_indexes_created")


# Query helpers for common patterns
class CosmosQueries:
    """Helper class for common database queries"""

    @staticmethod
    def find_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Find user by email"""
        client = get_cosmos_client()
        users = client.get_collection(CosmosCollections.USERS)
        return users.find_one({"email": email})

    @staticmethod
    def find_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Find user by ID"""
        client = get_cosmos_client()
        users = client.get_collection(CosmosCollections.USERS)
        return users.find_one({"id": user_id})

    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        client = get_cosmos_client()
        users = client.get_collection(CosmosCollections.USERS)

        # Add timestamps
        user_data["created_at"] = datetime.utcnow()
        user_data["updated_at"] = datetime.utcnow()

        result = users.insert_one(user_data)
        user_data["_id"] = result.inserted_id

        return user_data

    @staticmethod
    def update_user(user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user data"""
        client = get_cosmos_client()
        users = client.get_collection(CosmosCollections.USERS)

        updates["updated_at"] = datetime.utcnow()

        result = users.update_one(
            {"id": user_id},
            {"$set": updates}
        )

        return result.modified_count > 0

    @staticmethod
    def find_articles(
        source_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """Find articles with filters"""
        client = get_cosmos_client()
        articles = client.get_collection(CosmosCollections.ARTICLES)

        query = {}
        if source_id:
            query["source_id"] = source_id
        if status:
            query["processing_status"] = status

        return list(
            articles.find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )

    @staticmethod
    def create_article(article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new article"""
        client = get_cosmos_client()
        articles = client.get_collection(CosmosCollections.ARTICLES)

        article_data["created_at"] = datetime.utcnow()
        article_data["updated_at"] = datetime.utcnow()

        result = articles.insert_one(article_data)
        article_data["_id"] = result.inserted_id

        return article_data

    @staticmethod
    def find_chat_sessions(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Find chat sessions for a user"""
        client = get_cosmos_client()
        sessions = client.get_collection(CosmosCollections.CHAT_SESSIONS)

        return list(
            sessions.find({"user_id": user_id})
            .sort("created_at", -1)
            .limit(limit)
        )

    @staticmethod
    def find_chat_messages(session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Find messages for a chat session"""
        client = get_cosmos_client()
        messages = client.get_collection(CosmosCollections.CHAT_MESSAGES)

        return list(
            messages.find({"session_id": session_id})
            .sort("created_at", 1)
            .limit(limit)
        )


# Async context manager for database operations
class CosmosDBSession:
    """
    Context manager for Cosmos DB operations

    Usage:
        async with CosmosDBSession() as db:
            users = db.get_collection("users")
            user = users.find_one({"email": "test@example.com"})
    """

    def __init__(self):
        self.client: Optional[CosmosDBClient] = None

    def __enter__(self):
        self.client = get_cosmos_client()
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Don't close the client (it's a singleton)
        pass


if __name__ == "__main__":
    # Test connection
    try:
        client = get_cosmos_client()
        print(f"✅ Connected to Cosmos DB: {client.db_name}")
        print(f"Collections: {client.db.list_collection_names()}")

        # Create indexes
        create_indexes()
        print("✅ Indexes created")

    except Exception as e:
        print(f"❌ Error: {e}")
