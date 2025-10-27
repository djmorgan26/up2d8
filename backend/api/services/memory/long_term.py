"""
Layer 3: Long-Term Memory

Provides semantic search over all historical articles using vector embeddings.
Enables the agent to find relevant information from the entire knowledge base.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import structlog

from api.services.rag_service import RAGService

logger = structlog.get_logger()


class LongTermMemory:
    """
    Layer 3 Memory: Historical Knowledge Base

    Provides:
    - Semantic search over all articles (vector embeddings)
    - Historical context retrieval
    - Deep knowledge access

    Priority: MEDIUM (broader but less recent context)
    """

    def __init__(self, user_id: str, db: Session):
        """
        Initialize long-term memory

        Args:
            user_id: User ID
            db: Database session
        """
        self.user_id = user_id
        self.db = db

        # Initialize RAG service for vector search
        self.rag_service = RAGService()

        logger.info("long_term_memory_initialized", user_id=user_id)

    async def search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Semantic search over all historical articles

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of matching articles with relevance scores
        """
        # Use RAG service for semantic search
        rag_context = await self.rag_service.search_user_articles(
            user_id=self.user_id,
            query=query,
            top_k=top_k
        )

        results = [
            {
                "id": str(article.id),
                "title": article.title,
                "summary": article.summary_standard,
                "url": article.url,
                "source": article.source_id,
                "published_at": article.published_at.isoformat() if article.published_at else None,
                "relevance_score": score,
            }
            for article, score in zip(rag_context.articles, rag_context.relevance_scores)
        ]

        logger.info(
            "long_term_memory_search",
            user_id=self.user_id,
            query=query,
            results_count=len(results)
        )

        return results

    async def get_similar_articles(self, article_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find articles similar to a given article

        Args:
            article_id: Reference article ID
            top_k: Number of similar articles to return

        Returns:
            List of similar articles
        """
        similar_context = await self.rag_service.get_similar_articles(
            article_id=article_id,
            top_k=top_k
        )

        results = [
            {
                "id": str(article.id),
                "title": article.title,
                "summary": article.summary_standard,
                "url": article.url,
                "similarity_score": score,
            }
            for article, score in zip(similar_context.articles, similar_context.relevance_scores)
        ]

        logger.info(
            "long_term_memory_similar_articles",
            user_id=self.user_id,
            article_id=article_id,
            results_count=len(results)
        )

        return results

    async def get_context_for_query(self, query: str, num_articles: int = 3) -> str:
        """
        Get contextual information for a query as formatted text

        Args:
            query: User's question/query
            num_articles: Number of articles to include

        Returns:
            Formatted context string
        """
        results = await self.search(query=query, top_k=num_articles)

        if not results:
            return "No relevant historical articles found."

        context_parts = [
            f"Found {len(results)} relevant articles from your history:\n"
        ]

        for i, article in enumerate(results, 1):
            context_parts.append(
                f"{i}. {article['title']}\n"
                f"   Summary: {article['summary'][:150]}...\n"
                f"   Relevance: {article['relevance_score']:.2f}\n"
            )

        return "\n".join(context_parts)

    async def get_topic_articles(self, topic: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get articles related to a specific topic

        Args:
            topic: Topic to search for
            limit: Maximum number of articles

        Returns:
            Topic-related articles
        """
        return await self.search(query=topic, top_k=limit)

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "layer": "long_term",
            "user_id": self.user_id,
            "rag_service": "initialized",
            "vector_db_type": self.rag_service.vector_db.__class__.__name__,
        }


# Helper function for easy access
def get_long_term_memory(user_id: str, db: Session) -> LongTermMemory:
    """
    Get long-term memory for a user

    Args:
        user_id: User ID
        db: Database session

    Returns:
        LongTermMemory instance
    """
    return LongTermMemory(user_id=user_id, db=db)
