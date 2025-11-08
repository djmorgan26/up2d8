from fastapi import APIRouter, status, Depends
from dependencies import get_db_client
from datetime import datetime, UTC

router = APIRouter()

@router.get("/api/health", status_code=status.HTTP_200_OK)
async def health_check(db=Depends(get_db_client)):
    """
    Health check endpoint for monitoring system status.
    Returns database connection status and collection counts.
    """
    try:
        # Test database connection
        db.command('ping')

        # Get collection stats
        articles_count = db.articles.count_documents({})
        users_count = db.users.count_documents({})
        rss_feeds_count = db.rss_feeds.count_documents({})
        unprocessed_articles = db.articles.count_documents({"processed": False})

        return {
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "database": "connected",
            "collections": {
                "articles": {
                    "total": articles_count,
                    "unprocessed": unprocessed_articles
                },
                "users": users_count,
                "rss_feeds": rss_feeds_count
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat()
        }
