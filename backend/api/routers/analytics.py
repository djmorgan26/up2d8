"""
Analytics API endpoints for querying business insights.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import structlog

from api.db.session import get_db
from api.services.analytics_tracker import get_analytics_tracker
from api.utils.auth import get_current_user
from api.db.models import User

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/companies/top")
async def get_top_companies(
    limit: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Get top companies by user engagement.

    Returns companies ranked by popularity score, which considers:
    - Positive feedback count (weighted +2)
    - Negative feedback count (weighted -1)
    - Overall sentiment
    """
    analytics_tracker = get_analytics_tracker(db)
    return analytics_tracker.get_top_companies(limit=limit)


@router.get("/industries/top")
async def get_top_industries(
    limit: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Get top industries by user engagement.

    Returns industries ranked by popularity score.
    """
    analytics_tracker = get_analytics_tracker(db)
    return analytics_tracker.get_top_industries(limit=limit)


@router.get("/sources/performance")
async def get_source_performance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Get performance metrics for all sources.

    Returns:
    - Articles delivered from each source
    - Positive/negative feedback counts
    - Engagement rates
    """
    analytics_tracker = get_analytics_tracker(db)
    return analytics_tracker.get_source_performance()


@router.get("/daily/stats")
async def get_daily_stats(
    days: int = Query(default=7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Get daily aggregated statistics for trend analysis.

    Returns:
    - Digests sent per day
    - Articles delivered
    - Feedback received
    - Active users
    """
    analytics_tracker = get_analytics_tracker(db)
    return analytics_tracker.get_daily_stats(days=days)


@router.get("/summary")
async def get_analytics_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get a comprehensive analytics summary dashboard.

    Returns:
    - Top 5 companies
    - Top 5 industries
    - Source performance
    - Recent daily stats (last 7 days)
    """
    analytics_tracker = get_analytics_tracker(db)

    return {
        "top_companies": analytics_tracker.get_top_companies(limit=5),
        "top_industries": analytics_tracker.get_top_industries(limit=5),
        "source_performance": analytics_tracker.get_source_performance(),
        "daily_stats": analytics_tracker.get_daily_stats(days=7),
        "generated_at": str(datetime.now()),
    }


# Public endpoint for tracking article views (no auth required)
@router.post("/track/view")
async def track_article_view(
    article_id: str,
    user_id: str = None,
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """
    Track when a user clicks/views an article from their digest.

    This is called via tracking pixel or link click in emails.
    """
    try:
        # TODO: Implement click tracking when needed
        return {"status": "tracked", "article_id": article_id}
    except Exception as e:
        logger.error(f"Error tracking article view: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


from datetime import datetime
