"""
Relevance Scoring Service

Calculates relevance scores for articles based on:
- User preference match (explicit subscriptions)
- Engagement history (learned preferences from feedback)
- Article recency
- Article quality
- Diversity (avoid echo chamber)
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pymongo.database import Database
import structlog

from api.db.cosmos_db import CosmosCollections

logger = structlog.get_logger()


class RelevanceScorer:
    """
    Scores articles for personalized digest ranking.

    Scoring algorithm:
    relevance_score = (
        0.30 * preference_match_score +
        0.25 * engagement_score +
        0.20 * recency_score +
        0.15 * quality_score +
        0.10 * diversity_score
    )
    """

    # Scoring weights
    WEIGHT_PREFERENCE_MATCH = 0.30
    WEIGHT_ENGAGEMENT = 0.25
    WEIGHT_RECENCY = 0.20
    WEIGHT_QUALITY = 0.15
    WEIGHT_DIVERSITY = 0.10

    def __init__(self, db: Database, user: dict):
        self.db = db
        self.user = user
        self.preferences = self._get_user_preferences()
        self.preference_profile = self._get_preference_profile()

    def _get_user_preferences(self) -> Optional[dict]:
        """Get user's explicit preferences."""
        return self.db[CosmosCollections.USER_PREFERENCES].find_one(
            {"user_id": self.user["id"]}
        )

    def _get_preference_profile(self) -> Optional[dict]:
        """Get user's learned preference profile."""
        return self.db[CosmosCollections.USER_PREFERENCE_PROFILES].find_one(
            {"user_id": self.user["id"]}
        )

    def score_article(
        self, article: dict, already_included: List[str] = None
    ) -> Dict[str, float]:
        """
        Calculate relevance score for an article.

        Args:
            article: dict to score
            already_included: List of company/industry strings already in digest

        Returns:
            {
                "total_score": float (0-100),
                "preference_match_score": float (0-100),
                "engagement_score": float (0-100),
                "recency_score": float (0-100),
                "quality_score": float (0-100),
                "diversity_score": float (0-100),
            }
        """
        already_included = already_included or []

        # Calculate individual scores
        preference_score = self._calculate_preference_match_score(article)
        engagement_score = self._calculate_engagement_score(article)
        recency_score = self._calculate_recency_score(article)
        quality_score = self._calculate_quality_score(article)
        diversity_score = self._calculate_diversity_score(article, already_included)

        # Weighted total
        total_score = (
            self.WEIGHT_PREFERENCE_MATCH * preference_score
            + self.WEIGHT_ENGAGEMENT * engagement_score
            + self.WEIGHT_RECENCY * recency_score
            + self.WEIGHT_QUALITY * quality_score
            + self.WEIGHT_DIVERSITY * diversity_score
        )

        return {
            "total_score": round(total_score, 2),
            "preference_match_score": round(preference_score, 2),
            "engagement_score": round(engagement_score, 2),
            "recency_score": round(recency_score, 2),
            "quality_score": round(quality_score, 2),
            "diversity_score": round(diversity_score, 2),
        }

    def _calculate_preference_match_score(self, article: dict) -> float:
        """
        Score based on explicit user preferences.

        Scoring:
        - Exact company match: 100 points
        - Related industry match: 75 points
        - Technology/topic match: 50 points
        - Partial match: 25 points
        - No match: 0 points
        """
        if not self.preferences:
            return 50.0  # Neutral score if no preferences

        score = 0.0

        # Check company matches
        if self.preferences.get("subscribed_companies") and article.get("companies"):
            company_matches = set(self.preferences.get("subscribed_companies")) & set(
                article.get("companies")
            )
            if company_matches:
                score = max(score, 100.0)

        # Check industry matches
        if self.preferences.get("subscribed_industries") and article.get("industries"):
            industry_matches = set(self.preferences.get("subscribed_industries")) & set(
                article.get("industries")
            )
            if industry_matches:
                score = max(score, 75.0)

        # Check technology matches
        if self.preferences.get("subscribed_technologies") and article.get("technologies"):
            tech_matches = set(self.preferences.get("subscribed_technologies")) & set(
                article.get("technologies")
            )
            if tech_matches:
                score = max(score, 50.0)

        # Check people matches
        if self.preferences.get("subscribed_people") and article.get("people"):
            people_matches = set(self.preferences.get("subscribed_people")) & set(
                article.get("people")
            )
            if people_matches:
                score = max(score, 50.0)

        return score

    def _calculate_engagement_score(self, article: dict) -> float:
        """
        Score based on learned preferences from user feedback.

        Uses weights from UserPreferenceProfile to score articles.
        """
        if not self.preference_profile:
            return 50.0  # Neutral score if no learned preferences

        score = 0.0
        weight_count = 0

        # Score based on company weights
        if article.get("companies") and self.preference_profile.get("company_weights"):
            for company in article.get("companies"):
                weight = self.preference_profile.get("company_weights").get(company)
                if weight is not None:
                    score += weight * 100  # Convert 0-1 weight to 0-100 score
                    weight_count += 1

        # Score based on industry weights
        if article.get("industries") and self.preference_profile.get("industry_weights"):
            for industry in article.get("industries"):
                weight = self.preference_profile.get("industry_weights").get(industry)
                if weight is not None:
                    score += weight * 100
                    weight_count += 1

        # Score based on topic weights
        if article.get("categories") and self.preference_profile.get("topic_weights"):
            for topic in article.get("categories"):
                weight = self.preference_profile.get("topic_weights").get(topic)
                if weight is not None:
                    score += weight * 100
                    weight_count += 1

        # Average the scores if we found any weights
        if weight_count > 0:
            return score / weight_count

        return 50.0  # Neutral if no applicable weights found

    def _calculate_recency_score(self, article: dict) -> float:
        """
        Score based on how recent the article is.

        Scoring:
        - Last 6 hours: 100 points
        - 6-12 hours: 80 points
        - 12-18 hours: 60 points
        - 18-24 hours: 40 points
        - Older: decay exponentially
        """
        if not article.get("published_at"):
            return 50.0  # Neutral if no publish date

        now = datetime.utcnow()
        age_hours = (now - article.get("published_at")).total_seconds() / 3600

        if age_hours < 6:
            return 100.0
        elif age_hours < 12:
            return 80.0
        elif age_hours < 18:
            return 60.0
        elif age_hours < 24:
            return 40.0
        elif age_hours < 48:
            return 20.0
        else:
            # Exponential decay after 48 hours
            return max(0, 20.0 * (0.5 ** ((age_hours - 48) / 24)))

    def _calculate_quality_score(self, article: dict) -> float:
        """
        Score based on article quality.

        Uses existing quality_score field (0-1) and converts to 0-100.
        """
        if article.get("quality_score") is not None:
            return float(article.get("quality_score")) * 100

        # Fallback to impact score if quality score not available
        if article.get("impact_score") is not None:
            return article.get("impact_score") * 10  # Convert 1-10 to 10-100

        return 50.0  # Neutral if no quality metrics

    def _calculate_diversity_score(
        self, article: dict, already_included: List[str]
    ) -> float:
        """
        Score to promote diversity and avoid echo chamber.

        Penalize if:
        - Too many articles from same company already included
        - Same topics repeated

        Reward if:
        - Introduces new topics/companies
        """
        score = 100.0  # Start with perfect diversity score

        # Check if companies already heavily represented
        if article.get("companies"):
            for company in article.get("companies"):
                count_in_included = already_included.count(company)
                if count_in_included >= 3:
                    score -= 30  # Significant penalty for over-representation
                elif count_in_included >= 2:
                    score -= 15
                elif count_in_included >= 1:
                    score -= 5

        # Check if industries already heavily represented
        if article.get("industries"):
            for industry in article.get("industries"):
                count_in_included = already_included.count(industry)
                if count_in_included >= 2:
                    score -= 20
                elif count_in_included >= 1:
                    score -= 10

        # Ensure score stays in 0-100 range
        return max(0.0, min(100.0, score))


def score_articles_for_digest(
    db: Database, user: dict, articles: List[dict]
) -> List[tuple]:
    """
    Score a list of articles and return them sorted by relevance.

    Args:
        db: Database session
        user: User to score for (dict)
        articles: List of articles to score (dicts)

    Returns:
        List of (article, scores_dict) tuples sorted by total_score descending
    """
    scorer = RelevanceScorer(db, user)

    scored_articles = []
    already_included = []

    for article in articles:
        scores = scorer.score_article(article, already_included)
        scored_articles.append((article, scores))

        # Track what we've included for diversity scoring
        if article.get("companies"):
            already_included.extend(article.get("companies"))
        if article.get("industries"):
            already_included.extend(article.get("industries"))

    # Sort by total_score descending
    scored_articles.sort(key=lambda x: x[1]["total_score"], reverse=True)

    logger.info(
        "Scored articles for digest",
        user_id=user["id"],
        total_articles=len(articles),
        top_score=scored_articles[0][1]["total_score"] if scored_articles else 0,
    )

    return scored_articles
