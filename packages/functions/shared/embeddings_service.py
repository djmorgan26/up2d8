"""
Semantic search using Gemini Embeddings API.

Provides embeddings generation and cosine similarity calculation
for topic-based article matching.
"""

import google.generativeai as genai
from typing import List
import numpy as np
import structlog

logger = structlog.get_logger()


class EmbeddingsService:
    """Service for generating embeddings and calculating similarity."""

    def __init__(self, api_key: str):
        """Initialize the embeddings service with Gemini API key."""
        genai.configure(api_key=api_key)
        self.model_name = "models/text-embedding-004"

    def generate_embedding(self, text: str) -> List[float] | None:
        """
        Generate embedding vector for a text string.

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector, or None if error
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return None

        try:
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type="semantic_similarity"
            )
            return result['embedding']
        except Exception as e:
            logger.error("Failed to generate embedding", text_preview=text[:100], error=str(e))
            return None

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float] | None]:
        """
        Generate embeddings for multiple texts in a batch.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors (or None for failed embeddings)
        """
        embeddings = []
        for text in texts:
            embeddings.append(self.generate_embedding(text))
        return embeddings

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two embedding vectors.

        Args:
            vec1: First embedding vector
            vec2: Second embedding vector

        Returns:
            Similarity score between -1 and 1 (higher = more similar)
        """
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)

            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            return float(dot_product / (norm1 * norm2))
        except Exception as e:
            logger.error("Failed to calculate cosine similarity", error=str(e))
            return 0.0

    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two text strings.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score between -1 and 1 (higher = more similar)
        """
        emb1 = self.generate_embedding(text1)
        emb2 = self.generate_embedding(text2)

        if emb1 is None or emb2 is None:
            return 0.0

        return self.cosine_similarity(emb1, emb2)

    def rank_articles_by_topics(
        self,
        articles: List[dict],
        topic_embeddings: List[List[float]],
        recency_weight: float = 0.3
    ) -> List[tuple]:
        """
        Rank articles by semantic similarity to topic embeddings.

        Args:
            articles: List of article dicts (must have 'title', 'summary', 'created_at')
            topic_embeddings: List of embedding vectors for user topics
            recency_weight: Weight for recency scoring (0-1, default 0.3)

        Returns:
            List of (article, score) tuples sorted by descending score
        """
        if not topic_embeddings:
            logger.warning("No topic embeddings provided for ranking")
            return [(a, 0.0) for a in articles]

        ranked = []

        for article in articles:
            # Generate article embedding from title + summary
            article_text = f"{article.get('title', '')} {article.get('summary', '')}"
            article_embedding = self.generate_embedding(article_text)

            if article_embedding is None:
                ranked.append((article, 0.0))
                continue

            # Calculate max similarity to any topic
            max_similarity = 0.0
            for topic_emb in topic_embeddings:
                similarity = self.cosine_similarity(article_embedding, topic_emb)
                max_similarity = max(max_similarity, similarity)

            # Calculate recency score (0-1, newer = higher)
            from datetime import datetime, timedelta
            created_at = article.get('created_at')
            recency_score = 0.5  # Default for missing timestamps

            if created_at:
                if isinstance(created_at, str):
                    try:
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    except:
                        pass

                if isinstance(created_at, datetime):
                    age_hours = (datetime.utcnow() - created_at).total_seconds() / 3600
                    # Articles decay over 168 hours (7 days)
                    recency_score = max(0.0, 1.0 - (age_hours / 168.0))

            # Combine semantic similarity and recency
            final_score = (
                (1 - recency_weight) * max_similarity +
                recency_weight * recency_score
            )

            ranked.append((article, final_score))

        # Sort by score descending
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked
