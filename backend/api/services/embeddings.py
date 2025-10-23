"""
Embeddings Service with Free/Local and Paid Provider Support
"""
import os
from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np
from enum import Enum


class EmbeddingProvider(str, Enum):
    SENTENCE_TRANSFORMERS = "sentence-transformers"  # FREE - local
    OPENAI = "openai"  # PAID
    VOYAGE = "voyage"  # PAID


class BaseEmbeddingClient(ABC):
    """Abstract base class for embedding providers"""

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch of texts"""
        pass

    @abstractmethod
    def dimension(self) -> int:
        """Return embedding dimension"""
        pass


class SentenceTransformerClient(BaseEmbeddingClient):
    """
    Local sentence-transformers embeddings (FREE)
    Models:
    - all-MiniLM-L6-v2: 384 dims, fast, good quality
    - all-mpnet-base-v2: 768 dims, slower, better quality
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self._dimension = self.model.get_sentence_embedding_dimension()

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch of texts"""
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.tolist()

    def dimension(self) -> int:
        """Return embedding dimension"""
        return self._dimension


class OpenAIEmbeddingClient(BaseEmbeddingClient):
    """OpenAI embeddings (PAID - for production)"""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model
        # Dimensions by model
        self._dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch of texts"""
        response = self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        return [item.embedding for item in response.data]

    def dimension(self) -> int:
        """Return embedding dimension"""
        return self._dimensions.get(self.model, 1536)


class EmbeddingFactory:
    """Factory for creating embedding clients"""

    @staticmethod
    def create_client(
        provider: Optional[str] = None,
        model: Optional[str] = None
    ) -> BaseEmbeddingClient:
        """
        Create an embedding client based on environment configuration

        Args:
            provider: Override the configured provider
            model: Override the configured model

        Returns:
            BaseEmbeddingClient instance
        """
        provider = provider or os.getenv("EMBEDDING_PROVIDER", "sentence-transformers")

        if provider == EmbeddingProvider.SENTENCE_TRANSFORMERS:
            model = model or os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
            return SentenceTransformerClient(model_name=model)

        elif provider == EmbeddingProvider.OPENAI:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable required")
            model = model or os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
            return OpenAIEmbeddingClient(api_key=api_key, model=model)

        else:
            raise ValueError(f"Unsupported embedding provider: {provider}")


# Singleton instance
_embedding_client: Optional[BaseEmbeddingClient] = None


def get_embedding_client() -> BaseEmbeddingClient:
    """Get or create the global embedding client"""
    global _embedding_client
    if _embedding_client is None:
        _embedding_client = EmbeddingFactory.create_client()
    return _embedding_client
