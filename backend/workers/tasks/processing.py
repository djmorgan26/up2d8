"""
Celery tasks for article processing and AI summarization.

Tasks:
- process_article: Summarize a single article
- process_pending_articles: Process all pending articles in batch
"""

import asyncio
from datetime import datetime
from typing import Dict, Any
import structlog

from workers.celery_app import celery_app
from api.db.session import get_database
from api.db.cosmos_db import CosmosCollections
from api.services.summarizer import get_summarizer
from api.services.embeddings import get_embedding_client
from api.services.vector_db import get_vector_db

logger = structlog.get_logger()


@celery_app.task(bind=True, max_retries=2, default_retry_delay=300)
def process_article(self, article_id: str) -> Dict[str, Any]:
    """
    Process a single article with AI summarization.

    Args:
        article_id: UUID of article to process

    Returns:
        {
            "success": bool,
            "article_id": str,
            "summaries_generated": int,
            "processing_time": float,
            "timestamp": str
        }
    """
    db = get_database()
    start_time = datetime.utcnow()

    try:
        logger.info(f"Starting article processing for: {article_id}")

        # Get article from database
        article = db[CosmosCollections.ARTICLES].find_one({"id": article_id})

        if not article:
            raise ValueError(f"Article not found: {article_id}")

        if article.get("processing_status") == "completed":
            logger.info(f"Article {article_id} already processed, skipping")
            return {
                "success": True,
                "article_id": article_id,
                "summaries_generated": 0,
                "skipped": True,
                "reason": "already_processed",
            }

        # Update status to processing
        db[CosmosCollections.ARTICLES].update_one(
            {"id": article_id},
            {"$set": {"processing_status": "processing", "updated_at": datetime.utcnow()}}
        )

        # Generate summaries with timeout handling
        summarizer = get_summarizer()

        # Run async summarization in sync context
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        summaries = loop.run_until_complete(
            summarizer.summarize_article(
                title=article.get("title"),
                content=article.get("content") or "",
                author=article.get("author"),
                published_at=article.get("published_at"),
            )
        )

        # Count summaries generated (should be 1)
        summaries_generated = 1 if summaries.get("summary_standard") else 0

        # Update article with summary and mark as completed
        db[CosmosCollections.ARTICLES].update_one(
            {"id": article_id},
            {"$set": {
                "summary_standard": summaries.get("summary_standard"),
                "summary_micro": None,
                "summary_detailed": None,
                "processing_status": "completed",
                "updated_at": datetime.utcnow()
            }}
        )

        processing_time = (datetime.utcnow() - start_time).total_seconds()

        result = {
            "success": True,
            "article_id": article_id,
            "summaries_generated": summaries_generated,
            "processing_time": processing_time,
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info(
            f"Article processing completed for {article_id}",
            summaries_generated=summaries_generated,
            processing_time=processing_time,
        )

        return result

    except Exception as exc:
        logger.error(f"Error processing article {article_id}: {exc}", exc_info=True)

        # Update article status to failed
        try:
            db[CosmosCollections.ARTICLES].update_one(
                {"id": article_id},
                {"$set": {
                    "processing_status": "failed",
                    "updated_at": datetime.utcnow()
                }}
            )
        except Exception as e:
            logger.error(f"Failed to update article status: {e}")

        # Retry with exponential backoff
        raise self.retry(exc=exc)

    finally:
        db.close()


@celery_app.task(bind=True, name="workers.tasks.processing.process_pending_articles")
def process_pending_articles(self, limit: int = 50) -> Dict[str, Any]:
    """
    Process pending articles in batch.

    Args:
        limit: Maximum number of articles to process

    Returns:
        {
            "success": bool,
            "articles_processed": int,
            "articles_failed": int,
            "tasks_queued": list[str],
            "timestamp": str
        }
    """
    db = get_database()

    try:
        logger.info(f"Processing pending articles (limit: {limit})")

        # Get pending articles
        pending_articles = list(
            db[CosmosCollections.ARTICLES]
            .find({"processing_status": "pending"})
            .sort("fetched_at", -1)
            .limit(limit)
        )

        if not pending_articles:
            logger.info("No pending articles to process")
            return {
                "success": True,
                "articles_processed": 0,
                "articles_failed": 0,
                "tasks_queued": [],
                "timestamp": datetime.utcnow().isoformat(),
            }

        # Queue individual processing tasks
        tasks_queued = []
        for article in pending_articles:
            task = process_article.delay(article.get("id"))
            tasks_queued.append(
                {"article_id": article.get("id"), "task_id": task.id, "title": article.get("title")}
            )

        result = {
            "success": True,
            "articles_found": len(pending_articles),
            "tasks_queued": len(tasks_queued),
            "task_ids": [t["task_id"] for t in tasks_queued],
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info(
            f"Queued {len(tasks_queued)} article processing tasks",
            articles_found=len(pending_articles),
        )

        return result

    except Exception as exc:
        logger.error(f"Error processing pending articles: {exc}", exc_info=True)
        raise

    finally:
        db.close()


@celery_app.task(bind=True, max_retries=2)
def test_summarization(self) -> Dict[str, Any]:
    """
    Test summarization with a sample article to verify AI integration.

    Returns:
        {
            "success": bool,
            "test_article_title": str,
            "summaries": dict,
            "processing_time": float
        }
    """
    start_time = datetime.utcnow()

    try:
        logger.info("Running summarization test")

        # Test article
        test_title = "Anthropic Announces Claude 3.5 Sonnet"
        test_content = """
        Anthropic has announced Claude 3.5 Sonnet, the latest addition to its Claude AI family.
        The new model demonstrates significant improvements in reasoning, coding, and general
        intelligence tasks. Claude 3.5 Sonnet outperforms GPT-4 and Gemini 1.5 Pro on many
        benchmarks while maintaining the same cost and speed as Claude 3 Sonnet. Key features
        include enhanced coding capabilities, better understanding of complex instructions, and
        improved performance on graduate-level reasoning tasks. The model is now available via
        Anthropic's API and Claude.ai interface, marking a significant step forward in AI
        capabilities for businesses and developers.
        """

        # Generate summaries
        summarizer = get_summarizer()

        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        summaries = loop.run_until_complete(
            summarizer.summarize_article(
                title=test_title,
                content=test_content,
                author="Anthropic Team",
            )
        )

        processing_time = (datetime.utcnow() - start_time).total_seconds()

        result = {
            "success": True,
            "test_article_title": test_title,
            "summaries": summaries,
            "processing_time": processing_time,
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info(
            "Summarization test completed successfully",
            processing_time=processing_time,
            summary_length=len(summaries.get("summary_standard", "")),
            word_count=len(summaries.get("summary_standard", "").split()),
        )

        return result

    except Exception as exc:
        logger.error(f"Summarization test failed: {exc}", exc_info=True)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=300)
def embed_article(self, article_id: str) -> Dict[str, Any]:
    """
    Generate embeddings for an article and store in vector database.

    Args:
        article_id: UUID of article to embed

    Returns:
        {
            "success": bool,
            "article_id": str,
            "embedding_dimension": int,
            "processing_time": float,
            "timestamp": str
        }
    """
    db = get_database()
    start_time = datetime.utcnow()

    try:
        logger.info(f"Starting embedding generation for: {article_id}")

        # Get article from database
        article = db[CosmosCollections.ARTICLES].find_one({"id": article_id})

        if not article:
            raise ValueError(f"Article not found: {article_id}")

        if not article.get("summary_standard"):
            logger.warning(f"Article {article_id} has no summary, skipping embedding")
            return {
                "success": False,
                "article_id": article_id,
                "reason": "no_summary",
            }

        # Prepare text for embedding
        embedding_text = f"{article.get('title')}\n\n{article.get('summary_standard')}"
        if article.get("content") and len(article.get("content")) < 1000:
            embedding_text += f"\n\n{article.get('content')[:1000]}"

        # Generate embedding
        embedding_client = get_embedding_client()

        # Run async embedding in sync context
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        embedding = embedding_client.embed_text(embedding_text)

        # Store in vector database
        vector_db = get_vector_db()

        metadata = {
            "article_id": article_id,
            "title": article.get("title"),
            "source_id": article.get("source_id"),
            "published_at": article.get("published_at").isoformat() if article.get("published_at") else None,
            "companies": ",".join(article.get("companies")) if article.get("companies") else "",
            "industries": ",".join(article.get("industries")) if article.get("industries") else "",
        }

        loop.run_until_complete(
            vector_db.upsert(
                id=article_id,
                vector=embedding,
                metadata=metadata
            )
        )

        processing_time = (datetime.utcnow() - start_time).total_seconds()

        result = {
            "success": True,
            "article_id": article_id,
            "embedding_dimension": len(embedding),
            "processing_time": processing_time,
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info(
            f"Embedding completed for {article_id}",
            embedding_dimension=len(embedding),
            processing_time=processing_time,
        )

        return result

    except Exception as exc:
        logger.error(f"Error embedding article {article_id}: {exc}", exc_info=True)
        raise self.retry(exc=exc)

    finally:
        db.close()


@celery_app.task(bind=True, name="workers.tasks.processing.embed_pending_articles")
def embed_pending_articles(self, limit: int = 100) -> Dict[str, Any]:
    """
    Generate embeddings for articles that have summaries but no embeddings.

    Args:
        limit: Maximum number of articles to process

    Returns:
        {
            "success": bool,
            "articles_found": int,
            "tasks_queued": int,
            "task_ids": list[str],
            "timestamp": str
        }
    """
    db = get_database()

    try:
        logger.info(f"Embedding pending articles (limit: {limit})")

        # Get articles with summaries but not yet embedded
        # For now, we'll just process completed articles
        articles_to_embed = list(
            db[CosmosCollections.ARTICLES]
            .find({
                "processing_status": "completed",
                "summary_standard": {"$ne": None}
            })
            .sort("fetched_at", -1)
            .limit(limit)
        )

        if not articles_to_embed:
            logger.info("No articles to embed")
            return {
                "success": True,
                "articles_found": 0,
                "tasks_queued": 0,
                "task_ids": [],
                "timestamp": datetime.utcnow().isoformat(),
            }

        # Queue individual embedding tasks
        tasks_queued = []
        for article in articles_to_embed:
            task = embed_article.delay(article.get("id"))
            tasks_queued.append(task.id)

        result = {
            "success": True,
            "articles_found": len(articles_to_embed),
            "tasks_queued": len(tasks_queued),
            "task_ids": tasks_queued,
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info(
            f"Queued {len(tasks_queued)} embedding tasks",
            articles_found=len(articles_to_embed),
        )

        return result

    except Exception as exc:
        logger.error(f"Error embedding pending articles: {exc}", exc_info=True)
        raise

    finally:
        db.close()
