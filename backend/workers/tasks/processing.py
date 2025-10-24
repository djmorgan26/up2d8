"""Celery tasks for article processing (summarization, classification)."""

import logging
from datetime import datetime

from workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="workers.tasks.processing.process_pending_articles")
def process_pending_articles() -> dict:
    """Process articles with pending status.

    This will be implemented in Week 4 (AI Summarization).
    """
    logger.info("Process pending articles task (placeholder)")
    return {
        "success": True,
        "message": "Processing task placeholder - implement in Week 4",
        "timestamp": datetime.utcnow().isoformat(),
    }
