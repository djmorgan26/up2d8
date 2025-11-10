import logging
from datetime import UTC, datetime

from dependencies import get_db_client
from fastapi import APIRouter, Depends, status

router = APIRouter(tags=["System"])
logger = logging.getLogger(__name__)


@router.get("/api/health", status_code=status.HTTP_200_OK)
async def health_check(db=Depends(get_db_client)):
    """
    Health check endpoint for monitoring system status.

    Returns:
    - Service status (healthy/unhealthy)
    - Database connection status
    - Collection statistics (articles, users, RSS feeds)
    - API version and service info

    This endpoint is designed for monitoring tools and load balancers.
    """
    try:
        # Test database connection
        db_ping = db.command("ping")
        db_healthy = db_ping.get("ok") == 1

        # Get collection stats
        articles_count = db.articles.count_documents({})
        users_count = db.users.count_documents({})
        rss_feeds_count = db.rss_feeds.count_documents({})
        unprocessed_articles = db.articles.count_documents({"processed": False})

        return {
            "status": "healthy",
            "service": "UP2D8 Backend API",
            "version": "1.0.0",
            "timestamp": datetime.now(UTC).isoformat(),
            "database": {
                "status": "connected" if db_healthy else "error",
                "ping_ok": db_healthy
            },
            "collections": {
                "articles": {
                    "total": articles_count,
                    "unprocessed": unprocessed_articles,
                    "processed": articles_count - unprocessed_articles
                },
                "users": users_count,
                "rss_feeds": rss_feeds_count,
            },
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return {
            "status": "unhealthy",
            "service": "UP2D8 Backend API",
            "version": "1.0.0",
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat()
        }
