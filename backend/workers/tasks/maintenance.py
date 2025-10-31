"""Celery tasks for maintenance and cleanup."""

import logging
from datetime import datetime, timedelta

from workers.celery_app import celery_app
from api.db.session import get_database
from api.db.cosmos_db import CosmosCollections

logger = logging.getLogger(__name__)


@celery_app.task(name="workers.tasks.maintenance.cleanup_old_data")
def cleanup_old_data() -> dict:
    """Clean up old articles and data.

    Archives articles older than 1 year.
    """
    logger.info("Starting cleanup of old data")

    try:
        db = get_database()

        # Archive articles older than 1 year
        cutoff_date = datetime.utcnow() - timedelta(days=365)

        result = db[CosmosCollections.ARTICLES].update_many(
            {
                "published_at": {"$lt": cutoff_date},
                "processing_status": {"$ne": "archived"}
            },
            {"$set": {
                "processing_status": "archived",
                "updated_at": datetime.utcnow()
            }}
        )

        archived_count = result.modified_count

        return {
            "success": True,
            "articles_archived": archived_count,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error in cleanup task: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
