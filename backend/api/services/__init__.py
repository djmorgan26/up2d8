"""
UP2D8 Services Package
Provider abstractions for LLM, embeddings, vector DB, and email
"""
from api.services.llm_provider import get_llm_client
from api.services.embeddings import get_embedding_client
from api.services.vector_db import get_vector_db_client
from api.services.email_provider import get_email_client

__all__ = [
    "get_llm_client",
    "get_embedding_client",
    "get_vector_db_client",
    "get_email_client",
]
