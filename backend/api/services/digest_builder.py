"""
Digest Builder Service

Selects and organizes articles for daily email digests.
Considers user preferences, article relevance, and timing.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pymongo.database import Database
import structlog

from api.db.models import Collections
from api.db.cosmos_db import CosmosCollections

logger = structlog.get_logger()


class DigestBuilder:
    """
    Builds personalized daily digests for users.

    Selection criteria:
    - User's industry/company preferences
    - Article quality and relevance
    - Recent articles (last 24 hours)
    - Source authority
    """

    def __init__(self, db: Database):
        self.db = db

    def build_daily_digest(
        self,
        user: dict,
        max_articles: int = 10,
        hours_lookback: int = 24,
    ) -> Dict[str, Any]:
        """
        Build a daily digest for a user.

        Args:
            user: User dict from MongoDB
            max_articles: Maximum number of articles to include
            hours_lookback: How far back to look for articles (hours)

        Returns:
            {
                "user_id": str,
                "user_email": str,
                "user_name": str,
                "digest_date": str,
                "articles": [...],
                "article_count": int,
                "personalized": bool,
            }
        """
        user_id = user.get("id")
        logger.info(
            f"Building daily digest for user {user_id}",
            email=user.get("email"),
            max_articles=max_articles,
        )

        # Get user preferences
        preferences = self.db[CosmosCollections.USER_PREFERENCES].find_one(
            {"user_id": user_id}
        )

        # Calculate time window
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_lookback)

        # Build MongoDB query for articles
        article_query = {
            "processing_status": "completed",
            "fetched_at": {"$gte": cutoff_time},
            "summary_standard": {"$ne": None, "$exists": True},
        }

        # Apply personalization filters if preferences exist
        personalized = False
        if preferences:
            # Filter by user's subscribed companies/industries (MongoDB $in operator)
            subscribed_companies = preferences.get("subscribed_companies", [])
            subscribed_industries = preferences.get("subscribed_industries", [])

            if subscribed_companies or subscribed_industries:
                or_conditions = []
                if subscribed_companies:
                    or_conditions.append({"companies": {"$in": subscribed_companies}})
                if subscribed_industries:
                    or_conditions.append({"industries": {"$in": subscribed_industries}})

                article_query["$or"] = or_conditions
                personalized = True

        # Get candidate articles
        candidate_articles = list(
            self.db[CosmosCollections.ARTICLES]
            .find(article_query)
            .sort("published_at", -1)
            .limit(max_articles * 3)
        )

        logger.info(
            f"Found {len(candidate_articles)} candidate articles for digest",
            user_id=user_id,
            personalized=personalized,
        )

        # If no personalized results, get top recent articles
        if len(candidate_articles) == 0 and personalized:
            logger.info("No personalized articles found, falling back to top articles")
            candidate_articles = list(
                self.db[CosmosCollections.ARTICLES]
                .find({
                    "processing_status": "completed",
                    "fetched_at": {"$gte": cutoff_time},
                    "summary_standard": {"$ne": None, "$exists": True},
                })
                .sort("published_at", -1)
                .limit(max_articles * 2)
            )
            personalized = False

        # Simple scoring: take most recent articles
        # TODO: Implement proper relevance scoring
        articles = candidate_articles[:max_articles]

        # Format articles for digest
        formatted_articles = []
        for article in articles:
            # Get source info
            source = self.db[CosmosCollections.SOURCES].find_one(
                {"id": article.get("source_id")}
            )

            formatted_articles.append({
                "id": article.get("id"),
                "title": article.get("title"),
                "summary": article.get("summary_standard") or "No summary available.",
                "source": source.get("name") if source else "Unknown",
                "url": article.get("source_url"),
                "published_at": article.get("published_at").isoformat() if article.get("published_at") else None,
                "companies": article.get("companies", []),
                "industries": article.get("industries", []),
                "author": article.get("author"),
                "relevance_score": 1.0,  # TODO: Implement scoring
                "scoring_factors": {},
            })

        # Get base URL from environment (for feedback links)
        import os
        base_url = os.getenv("BASE_URL", "http://localhost:8000")

        digest = {
            "user_id": user_id,
            "user_email": user.get("email"),
            "user_name": user.get("full_name"),
            "digest_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "digest_day": datetime.utcnow().strftime("%A, %B %d, %Y"),
            "articles": formatted_articles,
            "article_count": len(formatted_articles),
            "personalized": personalized,
            "base_url": base_url,
        }

        logger.info(
            f"Built digest for {user.get('email')}",
            article_count=len(formatted_articles),
            personalized=personalized,
        )

        return digest

    def build_test_digest(self, user_email: str, user_name: str = "User") -> Dict[str, Any]:
        """
        Build a test digest with recent articles (using real user if found).

        Args:
            user_email: Email to send test to
            user_name: Name to use in email

        Returns:
            Digest dictionary
        """
        logger.info(f"Building test digest for {user_email}")

        # Try to find the user by email
        user = self.db[CosmosCollections.USERS].find_one({"email": user_email})
        if user:
            logger.info(f"Found user {user.get('id')} for test digest")
            user_id = user.get("id")
            user_name = user.get("full_name") or user_name
        else:
            logger.warning(f"User {user_email} not found, creating test digest without feedback tracking")
            user_id = None

        # Get recent completed articles
        cutoff_time = datetime.utcnow() - timedelta(hours=48)  # Last 2 days

        articles = list(
            self.db[CosmosCollections.ARTICLES]
            .find({
                "processing_status": "completed",
                "fetched_at": {"$gte": cutoff_time},
                "summary_standard": {"$ne": None, "$exists": True},
            })
            .sort("published_at", -1)
            .limit(10)
        )

        logger.info(f"Found {len(articles)} articles for test digest")

        # Format articles
        formatted_articles = []
        for article in articles:
            source = self.db[CosmosCollections.SOURCES].find_one(
                {"id": article.get("source_id")}
            )

            formatted_articles.append({
                "id": article.get("id"),
                "title": article.get("title"),
                "summary": article.get("summary_standard") or "No summary available.",
                "source": source.get("name") if source else "Unknown",
                "url": article.get("source_url"),
                "published_at": article.get("published_at").isoformat() if article.get("published_at") else None,
                "companies": article.get("companies", []),
                "industries": article.get("industries", []),
                "author": article.get("author"),
            })

        # Get base URL from environment (for feedback links)
        import os
        base_url = os.getenv("BASE_URL", "http://localhost:8000")

        digest = {
            "user_id": user_id,  # Now uses real user ID if found
            "user_email": user_email,
            "user_name": user_name,
            "digest_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "digest_day": datetime.utcnow().strftime("%A, %B %d, %Y"),
            "articles": formatted_articles,
            "article_count": len(formatted_articles),
            "personalized": False,
            "is_test": True,
            "base_url": base_url,
            "digest_id": "test",  # Test digests don't have a real digest record
        }

        return digest


def get_digest_builder(db: Database) -> DigestBuilder:
    """Factory function to get a DigestBuilder instance."""
    return DigestBuilder(db)
