"""API endpoints for scraping management."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from pydantic import BaseModel

from api.db.session import get_db
from api.db.models import Source, Article, User
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all content sources.

    Requires authentication.
    """
    query = db.query(Source)

    if active_only:
        query = query.filter(Source.active == True)

    if priority:
        query = query.filter(Source.priority == priority)

    sources = query.order_by(Source.priority.desc(), Source.name).all()

    return sources


@router.get("/sources/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get details for a specific source.

    Requires authentication.
    """
    source = db.query(Source).filter(Source.id == source_id).first()

    if not source:
        raise HTTPException(status_code=404, detail=f"Source not found: {source_id}")

    return source


@router.post("/sources/sync", response_model=dict)
async def sync_sources(
    current_user: User = Depends(get_current_user),
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually trigger scraping for a single source.

    Requires authentication.
    """
    # Verify source exists
    source = db.query(Source).filter(Source.id == source_id).first()

    if not source:
        raise HTTPException(status_code=404, detail=f"Source not found: {source_id}")

    # Dispatch scraping task
    task = scrape_source.delay(source_id)

    return {
        "task_id": task.id,
        "source_id": source_id,
        "message": f"Scraping task queued for {source.name}",
    }


@router.post("/scrape/all", response_model=ScrapeResultResponse)
async def trigger_scrape_all(
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List recently scraped articles.

    Requires authentication.
    """
    query = db.query(Article)

    if source_id:
        query = query.filter(Article.source_id == source_id)

    if status:
        query = query.filter(Article.processing_status == status)

    articles = (
        query.order_by(Article.fetched_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return articles


@router.get("/articles/stats")
async def get_article_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get statistics about scraped articles.

    Requires authentication.
    """
    from sqlalchemy import func

    total_articles = db.query(func.count(Article.id)).scalar()

    articles_by_status = (
        db.query(Article.processing_status, func.count(Article.id))
        .group_by(Article.processing_status)
        .all()
    )

    articles_by_source = (
        db.query(Source.name, func.count(Article.id))
        .join(Article, Source.id == Article.source_id)
        .group_by(Source.name)
        .order_by(func.count(Article.id).desc())
        .limit(10)
        .all()
    )

    return {
        "total_articles": total_articles,
        "by_status": {status: count for status, count in articles_by_status},
        "top_sources": [
            {"source": name, "count": count} for name, count in articles_by_source
        ],
    }


# ============================================================================
# Task Status Endpoints
# ============================================================================


@router.get("/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
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
    db: Session = Depends(get_db),
):
    """Health check for scraping system.

    No authentication required.
    """
    from datetime import datetime, timedelta

    # Check how many sources are active
    active_sources = db.query(func.count(Source.id)).filter(Source.active == True).scalar()

    # Check recent scraping activity (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_articles = (
        db.query(func.count(Article.id))
        .filter(Article.fetched_at >= yesterday)
        .scalar()
    )

    # Check for sources with recent failures
    failing_sources = (
        db.query(func.count(Source.id))
        .filter(Source.failure_count > 3, Source.active == True)
        .scalar()
    )

    return {
        "status": "healthy" if failing_sources == 0 else "degraded",
        "active_sources": active_sources,
        "articles_last_24h": recent_articles,
        "failing_sources": failing_sources,
    }
