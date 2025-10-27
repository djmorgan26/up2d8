"""
Layer 1: Digest Context Memory

Provides the agent with awareness of today's articles and recent digests.
This is the most recent and relevant context for answering user questions.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import structlog

from api.db.models import Article, Digest
from api.db.session import get_db

logger = structlog.get_logger()


class DigestContextMemory:
    """
    Layer 1 Memory: Today's Articles & Recent Digests

    Provides:
    - Today's scraped articles
    - Recent digest summaries
    - Quick access to "what's new"

    Priority: HIGHEST (most recent, most relevant)
    """

    def __init__(self, user_id: str, db: Session):
        """
        Initialize digest context memory

        Args:
            user_id: User ID to fetch personalized content
            db: Database session
        """
        self.user_id = user_id
        self.db = db
        self._cache: Dict[str, Any] = {}

        logger.info("digest_context_memory_initialized", user_id=user_id)

    def get_todays_articles(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get today's articles

        Args:
            limit: Maximum number of articles to return

        Returns:
            List of article dictionaries
        """
        # Check cache first
        cache_key = f"todays_articles_{limit}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Get articles from last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)

        articles = self.db.query(Article).filter(
            Article.fetched_at >= yesterday,
            Article.processing_status == "completed"
        ).order_by(
            Article.fetched_at.desc()
        ).limit(limit).all()

        # Convert to dictionaries
        result = [
            {
                "id": str(article.id),
                "title": article.title,
                "summary": article.summary_standard,
                "source": article.source_id,
                "url": article.url,
                "published_at": article.published_at.isoformat() if article.published_at else None,
                "fetched_at": article.fetched_at.isoformat() if article.fetched_at else None,
            }
            for article in articles
        ]

        # Cache for performance
        self._cache[cache_key] = result

        logger.info("todays_articles_fetched", count=len(result), user_id=self.user_id)

        return result

    def get_recent_digests(self, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get user's recent digests

        Args:
            limit: Maximum number of digests to return

        Returns:
            List of digest dictionaries
        """
        # Check cache
        cache_key = f"recent_digests_{limit}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        digests = self.db.query(Digest).filter(
            Digest.user_id == self.user_id,
            Digest.delivery_status == "sent"
        ).order_by(
            Digest.generated_at.desc()
        ).limit(limit).all()

        result = [
            {
                "id": str(digest.id),
                "generated_at": digest.generated_at.isoformat() if digest.generated_at else None,
                "article_count": digest.article_count or 0,
                "summary": digest.personalized_intro[:200] + "..." if digest.personalized_intro and len(digest.personalized_intro) > 200 else digest.personalized_intro,
            }
            for digest in digests
        ]

        self._cache[cache_key] = result

        logger.info("recent_digests_fetched", count=len(result), user_id=self.user_id)

        return result

    def get_context_summary(self) -> str:
        """
        Get a text summary of current digest context

        Returns:
            Summary string for the agent
        """
        articles = self.get_todays_articles(limit=10)
        digests = self.get_recent_digests(limit=2)

        summary_parts = []

        # Today's articles summary
        if articles:
            summary_parts.append(f"Today, you have {len(articles)} new articles:")
            for i, article in enumerate(articles[:5], 1):  # Top 5 only
                summary_parts.append(
                    f"{i}. {article['title']} (from {article['source']})"
                )
            if len(articles) > 5:
                summary_parts.append(f"...and {len(articles) - 5} more articles")
        else:
            summary_parts.append("No new articles today yet.")

        # Recent digests summary
        if digests:
            summary_parts.append(f"\nRecent digests ({len(digests)} total):")
            for digest in digests:
                summary_parts.append(
                    f"- Digest from {digest['generated_at'][:10] if digest['generated_at'] else 'unknown'} with {digest['article_count']} articles"
                )

        return "\n".join(summary_parts)

    def search_todays_articles(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search today's articles by keyword

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            Matching articles
        """
        articles = self.get_todays_articles(limit=50)  # Get more for searching

        # Simple keyword matching (can be enhanced with vector search)
        query_lower = query.lower()

        matching = [
            article for article in articles
            if query_lower in article['title'].lower()
            or (article['summary'] and query_lower in article['summary'].lower())
        ]

        return matching[:limit]

    def clear_cache(self):
        """Clear memory cache"""
        self._cache.clear()
        logger.info("digest_context_cache_cleared", user_id=self.user_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "layer": "digest_context",
            "user_id": self.user_id,
            "todays_articles_count": len(self.get_todays_articles()),
            "recent_digests_count": len(self.get_recent_digests()),
            "cache_size": len(self._cache),
        }


# Helper function for easy access
def get_digest_context(user_id: str, db: Session) -> DigestContextMemory:
    """
    Get digest context memory for a user

    Args:
        user_id: User ID
        db: Database session

    Returns:
        DigestContextMemory instance
    """
    return DigestContextMemory(user_id=user_id, db=db)
