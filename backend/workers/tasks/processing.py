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
from api.db.session import SessionLocal
from api.db.models import Article
from api.services.summarizer import get_summarizer

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
    db = SessionLocal()
    start_time = datetime.utcnow()

    try:
        logger.info(f"Starting article processing for: {article_id}")

        # Get article from database
        article = db.query(Article).filter(Article.id == article_id).first()

        if not article:
            raise ValueError(f"Article not found: {article_id}")

        if article.processing_status == "completed":
            logger.info(f"Article {article_id} already processed, skipping")
            return {
                "success": True,
                "article_id": article_id,
                "summaries_generated": 0,
                "skipped": True,
                "reason": "already_processed",
            }

        # Update status to processing
        article.processing_status = "processing"
        db.commit()

        # Generate summaries with timeout handling
        summarizer = get_summarizer()

        # Run async summarization in sync context
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        summaries = loop.run_until_complete(
            summarizer.summarize_article(
                title=article.title,
                content=article.content or "",
                author=article.author,
                published_at=article.published_at,
            )
        )

        # Update article with summary
        article.summary_standard = summaries.get("summary_standard")

        # Set other summary fields to None (single summary approach)
        article.summary_micro = None
        article.summary_detailed = None

        # Count summaries generated (should be 1)
        summaries_generated = 1 if article.summary_standard else 0

        # Mark as completed
        article.processing_status = "completed"
        article.updated_at = datetime.utcnow()
        db.commit()

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
            article = db.query(Article).filter(Article.id == article_id).first()
            if article:
                article.processing_status = "failed"
                article.updated_at = datetime.utcnow()
                db.commit()
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
    db = SessionLocal()

    try:
        logger.info(f"Processing pending articles (limit: {limit})")

        # Get pending articles
        pending_articles = (
            db.query(Article)
            .filter(Article.processing_status == "pending")
            .order_by(Article.fetched_at.desc())
            .limit(limit)
            .all()
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
            task = process_article.delay(article.id)
            tasks_queued.append(
                {"article_id": article.id, "task_id": task.id, "title": article.title}
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
