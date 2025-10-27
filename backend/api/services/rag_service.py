"""
RAG (Retrieval-Augmented Generation) Service for UP2D8

Provides semantic search and context retrieval for chat functionality.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import structlog

from api.services.embeddings import get_embedding_client
from api.services.vector_db import get_vector_db, VectorSearchResult
from api.db.session import SessionLocal
from api.db.models import Article

logger = structlog.get_logger()


class RAGContext:
    """Container for RAG retrieved context"""

    def __init__(
        self,
        articles: List[Article],
        relevance_scores: List[float],
        query: str,
    ):
        self.articles = articles
        self.relevance_scores = relevance_scores
        self.query = query

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "query": self.query,
            "articles_found": len(self.articles),
            "articles": [
                {
                    "id": article.id,
                    "title": article.title,
                    "summary": article.summary_standard,
                    "source_url": article.source_url,
                    "published_at": article.published_at.isoformat() if article.published_at else None,
                    "companies": article.companies,
                    "industries": article.industries,
                    "relevance_score": score,
                }
                for article, score in zip(self.articles, self.relevance_scores)
            ],
        }

    def format_for_llm(self) -> str:
        """Format context for LLM prompt"""
        if not self.articles:
            return "No relevant articles found."

        context_parts = []
        for i, article in enumerate(self.articles, 1):
            context_parts.append(
                f"[{i}] {article.title}\n"
                f"Source: {article.source_url}\n"
                f"Published: {article.published_at.strftime('%Y-%m-%d') if article.published_at else 'Unknown'}\n"
                f"Summary: {article.summary_standard}\n"
            )

        return "\n---\n".join(context_parts)


class RAGService:
    """Service for semantic search and context retrieval"""

    def __init__(self):
        self.embedding_client = get_embedding_client()
        self.vector_db = get_vector_db()

    async def search_articles(
        self,
        query: str,
        user_id: Optional[str] = None,
        top_k: int = 10,
        filter_companies: Optional[List[str]] = None,
        filter_industries: Optional[List[str]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> RAGContext:
        """
        Semantic search for articles relevant to the query.

        Args:
            query: User's search query
            user_id: Optional user ID for personalization
            top_k: Number of results to return
            filter_companies: Optional list of companies to filter by
            filter_industries: Optional list of industries to filter by
            date_from: Optional start date filter
            date_to: Optional end date filter

        Returns:
            RAGContext with retrieved articles
        """
        logger.info(
            "Performing semantic search",
            query=query,
            user_id=user_id,
            top_k=top_k,
        )

        try:
            # Generate query embedding
            query_embedding = self.embedding_client.embed_text(query)

            # Build filter dict for vector search
            filter_dict = {}
            # Note: ChromaDB requires string metadata, so filtering is limited
            # For more complex filtering, we'll post-process results

            # Perform vector search
            search_results: List[VectorSearchResult] = await self.vector_db.search(
                query_vector=query_embedding,
                top_k=top_k * 2,  # Get more results for post-filtering
                filter_dict=filter_dict if filter_dict else None,
            )

            if not search_results:
                logger.info("No articles found for query", query=query)
                return RAGContext(articles=[], relevance_scores=[], query=query)

            # Get article IDs
            article_ids = [result.id for result in search_results]

            # Fetch full articles from database
            db = SessionLocal()
            try:
                articles = (
                    db.query(Article)
                    .filter(Article.id.in_(article_ids))
                    .all()
                )

                # Create lookup for scores
                score_lookup = {result.id: result.score for result in search_results}

                # Apply additional filters
                filtered_articles = []
                filtered_scores = []

                for article in articles:
                    # Date filter
                    if date_from and article.published_at and article.published_at < date_from:
                        continue
                    if date_to and article.published_at and article.published_at > date_to:
                        continue

                    # Company filter
                    if filter_companies and article.companies:
                        if not any(company in article.companies for company in filter_companies):
                            continue

                    # Industry filter
                    if filter_industries and article.industries:
                        if not any(industry in article.industries for industry in filter_industries):
                            continue

                    filtered_articles.append(article)
                    filtered_scores.append(score_lookup.get(article.id, 0.0))

                # Sort by relevance score and limit to top_k
                sorted_pairs = sorted(
                    zip(filtered_articles, filtered_scores),
                    key=lambda x: x[1],
                    reverse=True,
                )[:top_k]

                if sorted_pairs:
                    final_articles, final_scores = zip(*sorted_pairs)
                    final_articles = list(final_articles)
                    final_scores = list(final_scores)
                else:
                    final_articles = []
                    final_scores = []

                logger.info(
                    "Semantic search completed",
                    query=query,
                    articles_found=len(final_articles),
                    top_score=final_scores[0] if final_scores else 0,
                )

                return RAGContext(
                    articles=final_articles,
                    relevance_scores=final_scores,
                    query=query,
                )

            finally:
                db.close()

        except Exception as e:
            logger.error("Error during semantic search", error=str(e), exc_info=True)
            raise

    async def search_user_articles(
        self,
        query: str,
        user_id: str,
        top_k: int = 5,
    ) -> RAGContext:
        """
        Search articles personalized for a specific user based on their preferences.

        Args:
            query: User's search query
            user_id: User ID
            top_k: Number of results to return

        Returns:
            RAGContext with retrieved articles
        """
        from api.db.models import User, UserPreference

        db = SessionLocal()
        try:
            # Get user preferences
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User not found: {user_id}")

            preferences = (
                db.query(UserPreference)
                .filter(UserPreference.user_id == user_id)
                .first()
            )

            # Extract user interests
            filter_companies = preferences.subscribed_companies if preferences and preferences.subscribed_companies else None
            filter_industries = preferences.subscribed_industries if preferences and preferences.subscribed_industries else None

            # Default to last 30 days
            date_from = datetime.utcnow() - timedelta(days=30)

            return await self.search_articles(
                query=query,
                user_id=user_id,
                top_k=top_k,
                filter_companies=filter_companies,
                filter_industries=filter_industries,
                date_from=date_from,
            )

        finally:
            db.close()

    async def get_similar_articles(
        self,
        article_id: str,
        top_k: int = 5,
    ) -> RAGContext:
        """
        Find articles similar to a given article.

        Args:
            article_id: ID of the reference article
            top_k: Number of similar articles to return

        Returns:
            RAGContext with similar articles
        """
        logger.info("Finding similar articles", article_id=article_id, top_k=top_k)

        db = SessionLocal()
        try:
            # Get the reference article
            article = db.query(Article).filter(Article.id == article_id).first()

            if not article:
                raise ValueError(f"Article not found: {article_id}")

            # Use article title and summary as query
            query = f"{article.title} {article.summary_standard or ''}"

            # Search for similar articles
            context = await self.search_articles(
                query=query,
                top_k=top_k + 1,  # +1 because the original article might be in results
            )

            # Filter out the original article
            filtered_articles = [a for a in context.articles if a.id != article_id]
            filtered_scores = [
                score
                for a, score in zip(context.articles, context.relevance_scores)
                if a.id != article_id
            ]

            return RAGContext(
                articles=filtered_articles[:top_k],
                relevance_scores=filtered_scores[:top_k],
                query=f"Similar to: {article.title}",
            )

        finally:
            db.close()


# Singleton instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get or create the global RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
