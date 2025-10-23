"""
Vector Database Abstraction Layer
Supports Chroma (free/local), pgvector (postgres extension), and Pinecone (paid)
"""
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid


class VectorDBProvider(str, Enum):
    CHROMA = "chroma"  # FREE - local
    PGVECTOR = "pgvector"  # FREE - postgres extension
    PINECONE = "pinecone"  # PAID


class VectorSearchResult:
    """Standardized search result"""

    def __init__(self, id: str, score: float, metadata: Dict[str, Any]):
        self.id = id
        self.score = score
        self.metadata = metadata


class BaseVectorDB(ABC):
    """Abstract base class for vector databases"""

    @abstractmethod
    async def upsert(
        self,
        id: str,
        vector: List[float],
        metadata: Dict[str, Any]
    ) -> None:
        """Insert or update a vector"""
        pass

    @abstractmethod
    async def upsert_batch(
        self,
        ids: List[str],
        vectors: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ) -> None:
        """Insert or update multiple vectors"""
        pass

    @abstractmethod
    async def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[VectorSearchResult]:
        """Search for similar vectors"""
        pass

    @abstractmethod
    async def delete(self, id: str) -> None:
        """Delete a vector by id"""
        pass

    @abstractmethod
    async def delete_batch(self, ids: List[str]) -> None:
        """Delete multiple vectors"""
        pass


class ChromaDB(BaseVectorDB):
    """
    ChromaDB vector database (FREE - local)
    Perfect for development, stores data locally
    """

    def __init__(self, persist_directory: str = "./data/chroma", collection_name: str = "articles"):
        import chromadb
        from chromadb.config import Settings

        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )

    async def upsert(
        self,
        id: str,
        vector: List[float],
        metadata: Dict[str, Any]
    ) -> None:
        """Insert or update a vector"""
        # Chroma requires string metadata values
        metadata_str = {k: str(v) for k, v in metadata.items()}

        self.collection.upsert(
            ids=[id],
            embeddings=[vector],
            metadatas=[metadata_str]
        )

    async def upsert_batch(
        self,
        ids: List[str],
        vectors: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ) -> None:
        """Insert or update multiple vectors"""
        # Convert metadata to strings
        metadatas_str = [
            {k: str(v) for k, v in metadata.items()}
            for metadata in metadatas
        ]

        self.collection.upsert(
            ids=ids,
            embeddings=vectors,
            metadatas=metadatas_str
        )

    async def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[VectorSearchResult]:
        """Search for similar vectors"""
        # Convert filter to Chroma format
        where_filter = None
        if filter_dict:
            where_filter = {k: str(v) for k, v in filter_dict.items()}

        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            where=where_filter
        )

        # Parse results
        search_results = []
        if results["ids"] and len(results["ids"]) > 0:
            for i, id_ in enumerate(results["ids"][0]):
                search_results.append(
                    VectorSearchResult(
                        id=id_,
                        score=1 - results["distances"][0][i],  # Convert distance to similarity
                        metadata=results["metadatas"][0][i] if results["metadatas"] else {}
                    )
                )

        return search_results

    async def delete(self, id: str) -> None:
        """Delete a vector by id"""
        self.collection.delete(ids=[id])

    async def delete_batch(self, ids: List[str]) -> None:
        """Delete multiple vectors"""
        self.collection.delete(ids=ids)


class PgVectorDB(BaseVectorDB):
    """
    PostgreSQL with pgvector extension (FREE)
    Uses existing Postgres database, no additional service needed
    """

    def __init__(self, connection_string: str, table_name: str = "embeddings"):
        from sqlalchemy import create_engine
        self.engine = create_engine(connection_string)
        self.table_name = table_name
        self._ensure_table()

    def _ensure_table(self):
        """Create embeddings table if it doesn't exist"""
        with self.engine.connect() as conn:
            # Enable pgvector extension
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            conn.commit()

            # Create embeddings table
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id TEXT PRIMARY KEY,
                    embedding VECTOR(384),  -- Adjust dimension as needed
                    metadata JSONB
                )
            """)
            conn.commit()

            # Create index for vector similarity search
            conn.execute(f"""
                CREATE INDEX IF NOT EXISTS {self.table_name}_embedding_idx
                ON {self.table_name}
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """)
            conn.commit()

    async def upsert(
        self,
        id: str,
        vector: List[float],
        metadata: Dict[str, Any]
    ) -> None:
        """Insert or update a vector"""
        import json
        with self.engine.connect() as conn:
            conn.execute(f"""
                INSERT INTO {self.table_name} (id, embedding, metadata)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                SET embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata
            """, (id, vector, json.dumps(metadata)))
            conn.commit()

    async def upsert_batch(
        self,
        ids: List[str],
        vectors: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ) -> None:
        """Insert or update multiple vectors"""
        import json
        with self.engine.connect() as conn:
            for id_, vector, metadata in zip(ids, vectors, metadatas):
                conn.execute(f"""
                    INSERT INTO {self.table_name} (id, embedding, metadata)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (id) DO UPDATE
                    SET embedding = EXCLUDED.embedding,
                        metadata = EXCLUDED.metadata
                """, (id_, vector, json.dumps(metadata)))
            conn.commit()

    async def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[VectorSearchResult]:
        """Search for similar vectors"""
        with self.engine.connect() as conn:
            # Build WHERE clause for filtering
            where_clause = ""
            if filter_dict:
                conditions = [
                    f"metadata->>'{k}' = '{v}'"
                    for k, v in filter_dict.items()
                ]
                where_clause = "WHERE " + " AND ".join(conditions)

            # Cosine similarity search
            result = conn.execute(f"""
                SELECT id, metadata, 1 - (embedding <=> %s::vector) as similarity
                FROM {self.table_name}
                {where_clause}
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (query_vector, query_vector, top_k))

            search_results = []
            for row in result:
                search_results.append(
                    VectorSearchResult(
                        id=row[0],
                        score=row[2],
                        metadata=row[1]
                    )
                )

            return search_results

    async def delete(self, id: str) -> None:
        """Delete a vector by id"""
        with self.engine.connect() as conn:
            conn.execute(f"DELETE FROM {self.table_name} WHERE id = %s", (id,))
            conn.commit()

    async def delete_batch(self, ids: List[str]) -> None:
        """Delete multiple vectors"""
        with self.engine.connect() as conn:
            conn.execute(
                f"DELETE FROM {self.table_name} WHERE id = ANY(%s)",
                (ids,)
            )
            conn.commit()


class PineconeDB(BaseVectorDB):
    """
    Pinecone vector database (PAID - for production)
    Managed service with excellent performance
    """

    def __init__(self, api_key: str, environment: str, index_name: str):
        import pinecone
        pinecone.init(api_key=api_key, environment=environment)
        self.index = pinecone.Index(index_name)

    async def upsert(
        self,
        id: str,
        vector: List[float],
        metadata: Dict[str, Any]
    ) -> None:
        """Insert or update a vector"""
        self.index.upsert(vectors=[(id, vector, metadata)])

    async def upsert_batch(
        self,
        ids: List[str],
        vectors: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ) -> None:
        """Insert or update multiple vectors"""
        vectors_with_metadata = [
            (id_, vector, metadata)
            for id_, vector, metadata in zip(ids, vectors, metadatas)
        ]
        self.index.upsert(vectors=vectors_with_metadata, batch_size=100)

    async def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[VectorSearchResult]:
        """Search for similar vectors"""
        results = self.index.query(
            vector=query_vector,
            top_k=top_k,
            filter=filter_dict,
            include_metadata=True
        )

        search_results = []
        for match in results.matches:
            search_results.append(
                VectorSearchResult(
                    id=match.id,
                    score=match.score,
                    metadata=match.metadata
                )
            )

        return search_results

    async def delete(self, id: str) -> None:
        """Delete a vector by id"""
        self.index.delete(ids=[id])

    async def delete_batch(self, ids: List[str]) -> None:
        """Delete multiple vectors"""
        self.index.delete(ids=ids)


class VectorDBFactory:
    """Factory for creating vector database clients"""

    @staticmethod
    def create_client(provider: Optional[str] = None) -> BaseVectorDB:
        """
        Create a vector database client based on environment configuration

        Args:
            provider: Override the configured provider

        Returns:
            BaseVectorDB instance
        """
        provider = provider or os.getenv("VECTOR_DB_PROVIDER", "chroma")

        if provider == VectorDBProvider.CHROMA:
            persist_dir = os.getenv("CHROMA_PATH", "./data/chroma")
            return ChromaDB(persist_directory=persist_dir)

        elif provider == VectorDBProvider.PGVECTOR:
            conn_string = os.getenv("DATABASE_URL")
            if not conn_string:
                raise ValueError("DATABASE_URL environment variable required for pgvector")
            return PgVectorDB(connection_string=conn_string)

        elif provider == VectorDBProvider.PINECONE:
            api_key = os.getenv("PINECONE_API_KEY")
            environment = os.getenv("PINECONE_ENVIRONMENT")
            index_name = os.getenv("PINECONE_INDEX_NAME")

            if not all([api_key, environment, index_name]):
                raise ValueError("PINECONE_API_KEY, PINECONE_ENVIRONMENT, and PINECONE_INDEX_NAME required")

            return PineconeDB(
                api_key=api_key,
                environment=environment,
                index_name=index_name
            )

        else:
            raise ValueError(f"Unsupported vector database provider: {provider}")


# Singleton instance
_vector_db_client: Optional[BaseVectorDB] = None


def get_vector_db() -> BaseVectorDB:
    """Get or create the global vector database client"""
    global _vector_db_client
    if _vector_db_client is None:
        _vector_db_client = VectorDBFactory.create_client()
    return _vector_db_client
