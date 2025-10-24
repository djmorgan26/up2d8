"""Celery tasks for digest generation and delivery."""

import logging
from datetime import datetime

from workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="workers.tasks.digests.generate_scheduled_digests")
def generate_scheduled_digests() -> dict:
    """Generate and send scheduled digests.

    This will be implemented in Week 5-7 (Digest Generation & Delivery).
    """
    logger.info("Generate scheduled digests task (placeholder)")
    return {
        "success": True,
        "message": "Digest generation task placeholder - implement in Week 5-7",
        "timestamp": datetime.utcnow().isoformat(),
    }
