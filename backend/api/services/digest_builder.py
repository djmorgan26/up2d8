"""
Digest Builder Service

Selects and organizes articles for daily email digests.
Considers user preferences, article relevance, and timing.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import structlog

from api.db.models import Article, User, UserPreference, Source
from api.services.relevance_scorer import score_articles_for_digest

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

    def __init__(self, db: Session):
        self.db = db

    def build_daily_digest(
        self,
        user: User,
        max_articles: int = 10,
        hours_lookback: int = 24,
    ) -> Dict[str, Any]:
        """
        Build a daily digest for a user.

        Args:
            user: User to build digest for
            max_articles: Maximum number of articles to include
            hours_lookback: How far back to look for articles (hours)

        Returns:
            {
                "user_id": str,
                "user_email": str,
                "user_name": str,
                "digest_date": str,
                "articles": [
                    {
                        "id": str,
                        "title": str,
                        "summary": str,
                        "source": str,
                        "url": str,
                        "published_at": str,
                        "companies": list,
                        "industries": list,
                    }
                ],
                "article_count": int,
                "personalized": bool,
            }
        """
        logger.info(
            f"Building daily digest for user {user.id}",
            email=user.email,
            max_articles=max_articles,
        )

        # Get user preferences
        preferences = (
            self.db.query(UserPreference)
            .filter(UserPreference.user_id == user.id)
            .first()
        )

        # Calculate time window
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_lookback)

        # Build query for articles
        query = (
            self.db.query(Article)
            .filter(
                and_(
                    Article.processing_status == "completed",
                    Article.fetched_at >= cutoff_time,
                    Article.summary_standard.isnot(None),
                )
            )
        )

        # Apply personalization filters if preferences exist
        personalized = False
        if preferences:
            # Filter by user's subscribed companies (using PostgreSQL && overlap operator)
            if preferences.subscribed_companies:
                query = query.filter(
                    Article.companies.op('&&')(preferences.subscribed_companies)
                )
                personalized = True

            # Filter by user's subscribed industries (using PostgreSQL && overlap operator)
            if preferences.subscribed_industries:
                query = query.filter(
                    Article.industries.op('&&')(preferences.subscribed_industries)
                )
                personalized = True

        # Get candidate articles (fetch more than needed for scoring)
        candidate_articles = (
            query.order_by(Article.published_at.desc())
            .limit(max_articles * 3)  # Fetch 3x to have pool for scoring
            .all()
        )

        logger.info(
            f"Found {len(candidate_articles)} candidate articles for digest",
            user_id=user.id,
            personalized=personalized,
        )

        # If no personalized results, get top articles from high-authority sources
        if len(candidate_articles) == 0 and personalized:
            logger.info("No personalized articles found, falling back to top articles")
            candidate_articles = (
                self.db.query(Article)
                .join(Source, Article.source_id == Source.id)
                .filter(
                    and_(
                        Article.processing_status == "completed",
                        Article.fetched_at >= cutoff_time,
                        Article.summary_standard.isnot(None),
                    )
                )
                .order_by(Source.authority_score.desc(), Article.published_at.desc())
                .limit(max_articles * 2)
                .all()
            )
            personalized = False

        # Score articles using relevance scorer
        scored_articles = score_articles_for_digest(self.db, user, candidate_articles)

        # Take top N by relevance score
        articles = [article for article, scores in scored_articles[:max_articles]]
        article_scores = {
            article.id: scores for article, scores in scored_articles[:max_articles]
        }

        # Format articles for digest
        formatted_articles = []
        for article in articles:
            # Get source info
            source = self.db.query(Source).filter(Source.id == article.source_id).first()

            # Get relevance scores for this article
            scores = article_scores.get(article.id, {})

            formatted_articles.append({
                "id": article.id,
                "title": article.title,
                "summary": article.summary_standard or article.summary_micro or "No summary available.",
                "source": source.name if source else "Unknown",
                "url": article.source_url,
                "published_at": article.published_at.isoformat() if article.published_at else None,
                "companies": article.companies or [],
                "industries": article.industries or [],
                "author": article.author,
                "relevance_score": scores.get("total_score", 0),
                "scoring_factors": scores,  # Include all scoring components
            })

        digest = {
            "user_id": user.id,
            "user_email": user.email,
            "user_name": user.full_name,
            "digest_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "digest_day": datetime.utcnow().strftime("%A, %B %d, %Y"),
            "articles": formatted_articles,
            "article_count": len(formatted_articles),
            "personalized": personalized,
        }

        logger.info(
            f"Built digest for {user.email}",
            article_count=len(formatted_articles),
            personalized=personalized,
        )

        return digest

    def build_test_digest(self, user_email: str, user_name: str = "User") -> Dict[str, Any]:
        """
        Build a test digest with recent articles (no user object needed).

        Args:
            user_email: Email to send test to
            user_name: Name to use in email

        Returns:
            Digest dictionary
        """
        logger.info(f"Building test digest for {user_email}")

        # Get recent completed articles
        cutoff_time = datetime.utcnow() - timedelta(hours=48)  # Last 2 days

        articles = (
            self.db.query(Article)
            .join(Source, Article.source_id == Source.id)
            .filter(
                and_(
                    Article.processing_status == "completed",
                    Article.fetched_at >= cutoff_time,
                    Article.summary_standard.isnot(None),
                )
            )
            .order_by(Source.authority_score.desc(), Article.published_at.desc())
            .limit(10)
            .all()
        )

        logger.info(f"Found {len(articles)} articles for test digest")

        # Format articles
        formatted_articles = []
        for article in articles:
            source = self.db.query(Source).filter(Source.id == article.source_id).first()

            formatted_articles.append({
                "id": article.id,
                "title": article.title,
                "summary": article.summary_standard or article.summary_micro or "No summary available.",
                "source": source.name if source else "Unknown",
                "url": article.source_url,
                "published_at": article.published_at.isoformat() if article.published_at else None,
                "companies": article.companies or [],
                "industries": article.industries or [],
                "author": article.author,
            })

        digest = {
            "user_id": "test",
            "user_email": user_email,
            "user_name": user_name,
            "digest_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "digest_day": datetime.utcnow().strftime("%A, %B %d, %Y"),
            "articles": formatted_articles,
            "article_count": len(formatted_articles),
            "personalized": False,
            "is_test": True,
        }

        return digest


def get_digest_builder(db: Session) -> DigestBuilder:
    """Factory function to get a DigestBuilder instance."""
    return DigestBuilder(db)
