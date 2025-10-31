"""API endpoints for scraping management."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pymongo.database import Database
from pydantic import BaseModel

from api.db.session import get_db
from api.utils.auth import get_current_user
from workers.tasks.scraping import (
    scrape_source,
    scrape_all_sources,
    scrape_priority_sources,
    sync_sources_to_db,
)

router = APIRouter(prefix="/api/v1/scraping", tags=["scraping"])


# ============================================================================
# Response Models
# ============================================================================


class SourceResponse(BaseModel):
    """Response model for source information."""

    id: str
    name: str
    type: str
    url: str
    check_interval_hours: int
    priority: str
    authority_score: int
    active: bool
    success_count: int
    failure_count: int
    last_checked_at: Optional[str]
    next_check_at: Optional[str]

    class Config:
        from_attributes = True


class ArticleResponse(BaseModel):
    """Response model for article information."""

    id: str
    source_id: str
    title: str
    source_url: str
    published_at: Optional[str]
    fetched_at: str
    processing_status: str
    companies: List[str]
    industries: List[str]

    class Config:
        from_attributes = True


class ScrapeTaskResponse(BaseModel):
    """Response model for scrape task."""

    task_id: str
    source_id: str
    message: str


class ScrapeResultResponse(BaseModel):
    """Response model for scrape results."""

    success: bool
    message: str
    tasks: Optional[List[dict]] = None
    articles_scraped: Optional[int] = None
    articles_stored: Optional[int] = None
    duplicates_found: Optional[int] = None


# ============================================================================
# Source Management Endpoints
# ============================================================================


@router.get("/sources", response_model=List[SourceResponse])
async def list_sources(
    active_only: bool = Query(True, description="Show only active sources"),
    priority: Optional[str] = Query(None, description="Filter by priority (high, medium, low)"),
    db: Database = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List all content sources.

    Requires authentication.
    """
    from api.db.cosmos_db import CosmosCollections

    # Build MongoDB query
    query_filter = {}
    if active_only:
        query_filter["active"] = True
    if priority:
        query_filter["priority"] = priority

    # Fetch sources
    sources = list(
        db[CosmosCollections.SOURCES]
        .find(query_filter)
        .sort([("priority", -1), ("name", 1)])
    )

    return sources


@router.get("/sources/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: str,
    db: Database = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get details for a specific source.

    Requires authentication.
    """
    from api.db.cosmos_db import CosmosCollections

    source = db[CosmosCollections.SOURCES].find_one({"id": source_id})

    if not source:
        raise HTTPException(status_code=404, detail=f"Source not found: {source_id}")

    return source


@router.post("/sources/sync", response_model=dict)
async def sync_sources(
    current_user: dict = Depends(get_current_user),
):
    """Sync sources from YAML config to database.

    Requires authentication.
    Useful for initial setup or after modifying sources.yaml.
    """
    task = sync_sources_to_db.delay()

    return {
        "task_id": task.id,
        "message": "Source sync task queued",
        "status_url": f"/api/v1/scraping/tasks/{task.id}",
    }


# ============================================================================
# Scraping Control Endpoints
# ============================================================================


@router.post("/scrape/{source_id}", response_model=ScrapeTaskResponse)
async def trigger_scrape_single(
    source_id: str,
    db: Database = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Manually trigger scraping for a single source.

    Requires authentication.
    """
    from api.db.cosmos_db import CosmosCollections

    # Verify source exists
    source = db[CosmosCollections.SOURCES].find_one({"id": source_id})

    if not source:
        raise HTTPException(status_code=404, detail=f"Source not found: {source_id}")

    # Dispatch scraping task
    task = scrape_source.delay(source_id)

    return {
        "task_id": task.id,
        "source_id": source_id,
        "message": f"Scraping task queued for {source['name']}",
    }


@router.post("/scrape/all", response_model=ScrapeResultResponse)
async def trigger_scrape_all(
    current_user: dict = Depends(get_current_user),
):
    """Manually trigger scraping for all active sources.

    Requires authentication.
    Use with caution - will dispatch many tasks.
    """
    task = scrape_all_sources.delay()

    return {
        "success": True,
        "message": "Scraping queued for all active sources",
        "tasks": [{"task_id": task.id, "type": "batch_scrape"}],
    }


@router.post("/scrape/priority/{priority}", response_model=ScrapeResultResponse)
async def trigger_scrape_by_priority(
    priority: str = Path(..., regex="^(high|medium|low)$"),
    current_user: dict = Depends(get_current_user),
):
    """Manually trigger scraping for sources of a specific priority.

    Requires authentication.
    Priority must be: high, medium, or low.
    """
    task = scrape_priority_sources.delay(priority)

    return {
        "success": True,
        "message": f"Scraping queued for {priority} priority sources",
        "tasks": [{"task_id": task.id, "priority": priority}],
    }


# ============================================================================
# Articles Endpoints
# ============================================================================


@router.get("/articles", response_model=List[ArticleResponse])
async def list_articles(
    limit: int = Query(50, ge=1, le=200, description="Number of articles to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    source_id: Optional[str] = Query(None, description="Filter by source ID"),
    status: Optional[str] = Query(None, description="Filter by processing status"),
    db: Database = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List recently scraped articles.

    Requires authentication.
    """
    from api.db.cosmos_db import CosmosCollections

    # Build MongoDB query
    query_filter = {}
    if source_id:
        query_filter["source_id"] = source_id
    if status:
        query_filter["processing_status"] = status

    # Fetch articles
    articles = list(
        db[CosmosCollections.ARTICLES]
        .find(query_filter)
        .sort("fetched_at", -1)
        .skip(offset)
        .limit(limit)
    )

    return articles


@router.get("/articles/stats")
async def get_article_stats(
    db: Database = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get statistics about scraped articles.

    Requires authentication.
    """
    from api.db.cosmos_db import CosmosCollections

    # Total articles
    total_articles = db[CosmosCollections.ARTICLES].count_documents({})

    # Articles by status (aggregation)
    by_status_pipeline = [
        {"$group": {"_id": "$processing_status", "count": {"$sum": 1}}}
    ]
    by_status_results = list(db[CosmosCollections.ARTICLES].aggregate(by_status_pipeline))
    articles_by_status = {item["_id"]: item["count"] for item in by_status_results}

    # Articles by source (aggregation with lookup)
    by_source_pipeline = [
        {"$group": {"_id": "$source_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    by_source_results = list(db[CosmosCollections.ARTICLES].aggregate(by_source_pipeline))

    # Fetch source names
    top_sources = []
    for item in by_source_results:
        source = db[CosmosCollections.SOURCES].find_one({"id": item["_id"]})
        top_sources.append({
            "source": source["name"] if source else item["_id"],
            "count": item["count"]
        })

    return {
        "total_articles": total_articles,
        "by_status": articles_by_status,
        "top_sources": top_sources,
    }


# ============================================================================
# Task Status Endpoints
# ============================================================================


@router.get("/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get status of a Celery task.

    Requires authentication.
    """
    from celery.result import AsyncResult
    from workers.celery_app import celery_app

    task = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": task.state,
        "result": task.result if task.ready() else None,
        "info": task.info if not task.ready() else None,
    }


# ============================================================================
# Health Check
# ============================================================================


@router.get("/health")
async def scraping_health(
    db: Database = Depends(get_db),
):
    """Health check for scraping system.

    No authentication required.
    """
    from datetime import datetime, timedelta
    from api.db.cosmos_db import CosmosCollections

    # Check how many sources are active
    active_sources = db[CosmosCollections.SOURCES].count_documents({"active": True})

    # Check recent scraping activity (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_articles = db[CosmosCollections.ARTICLES].count_documents(
        {"fetched_at": {"$gte": yesterday}}
    )

    # Check for sources with recent failures
    failing_sources = db[CosmosCollections.SOURCES].count_documents(
        {"failure_count": {"$gt": 3}, "active": True}
    )

    return {
        "status": "healthy" if failing_sources == 0 else "degraded",
        "active_sources": active_sources,
        "articles_last_24h": recent_articles,
        "failing_sources": failing_sources,
    }
