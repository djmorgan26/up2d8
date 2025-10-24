"""
UP2D8 Services Package
Provider abstractions for LLM, embeddings, vector DB, email, and scraping
"""

# Lazy imports to avoid circular dependencies
# Import only when needed

__all__ = [
    "get_llm_client",
    "get_embedding_client",
    "get_vector_db_client",
    "get_email_client",
    "create_scraper",
    "SourceManager",
    "get_summarizer",
]

def get_llm_client(*args, **kwargs):
    from api.services.llm_provider import get_llm_client as _get_llm_client
    return _get_llm_client(*args, **kwargs)

def get_embedding_client(*args, **kwargs):
    from api.services.embeddings import get_embedding_client as _get_embedding_client
    return _get_embedding_client(*args, **kwargs)

def get_vector_db_client(*args, **kwargs):
    from api.services.vector_db import get_vector_db_client as _get_vector_db_client
    return _get_vector_db_client(*args, **kwargs)

def get_email_client(*args, **kwargs):
    from api.services.email_provider import get_email_client as _get_email_client
    return _get_email_client(*args, **kwargs)

def get_summarizer(*args, **kwargs):
    from api.services.summarizer import get_summarizer as _get_summarizer
    return _get_summarizer(*args, **kwargs)
