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
    db: Database = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Sync sources from YAML config to database.

    Requires authentication.
    Useful for initial setup or after modifying sources.yaml.
    """
    from api.services.scraping_sync import sync_sources_to_db

    # Call synchronous function directly (no Celery)
    result = sync_sources_to_db()

    return result


@router.post("/sources/sync/direct", response_model=dict)
async def sync_sources_direct(
    db: Database = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Sync sources from YAML config to database directly (for testing/demo).

    Requires authentication.
    """
    from api.db.cosmos_db import CosmosCollections
    from api.db.models import SourceDocument
    from datetime import datetime
    import yaml
    from pathlib import Path

    try:
        # Load sources from YAML
        config_file = Path(__file__).parent.parent.parent / "config" / "sources.yaml"

        with open(config_file, "r") as f:
            data = yaml.safe_load(f)
            yaml_sources = data.get("sources", [])

        created_count = 0
        updated_count = 0

        for source_config in yaml_sources:
            try:
                # Check if source exists
                source_record = db[CosmosCollections.SOURCES].find_one(
                    {"id": source_config["id"]}
                )

                if source_record:
                    # Update existing source
                    db[CosmosCollections.SOURCES].update_one(
                        {"id": source_config["id"]},
                        {
                            "$set": {
                                "name": source_config["name"],
                                "type": source_config["type"],
                                "url": source_config.get("url", ""),
                                "config": source_config.get("config", {}),
                                "check_interval_hours": source_config.get(
                                    "check_interval_hours", 6
                                ),
                                "priority": source_config.get("priority", "medium"),
                                "authority_score": source_config.get("authority_score", 50),
                                "companies": source_config.get("companies", []),
                                "industries": source_config.get("industries", []),
                                "active": source_config.get("active", True),
                                "updated_at": datetime.utcnow(),
                            }
                        }
                    )
                    updated_count += 1
                else:
                    # Create new source
                    new_source = SourceDocument.create(
                        source_id=source_config["id"],
                        name=source_config["name"],
                        source_type=source_config["type"],
                        url=source_config.get("url", ""),
                        config=source_config.get("config", {}),
                        check_interval_hours=source_config.get("check_interval_hours", 6),
                        priority=source_config.get("priority", "medium"),
                        authority_score=source_config.get("authority_score", 50),
                        companies=source_config.get("companies", []),
                        industries=source_config.get("industries", []),
                        active=source_config.get("active", True),
                    )
                    db[CosmosCollections.SOURCES].insert_one(new_source)
                    created_count += 1

            except Exception as e:
                print(f"Error syncing source {source_config['id']}: {e}")
                continue

        return {
            "success": True,
            "message": "Sources synced successfully",
            "sources_created": created_count,
            "sources_updated": updated_count,
            "total_sources": len(yaml_sources),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


# ============================================================================
# Scraping Control Endpoints
# ============================================================================


@router.post("/scrape/{source_id}", response_model=dict)
async def trigger_scrape_single(
    source_id: str,
    db: Database = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Manually trigger scraping for a single source.

    Requires authentication.
    """
    from api.services.scraping_sync import scrape_source_sync

    # Call async function directly (no Celery)
    result = await scrape_source_sync(source_id)

    return result


@router.post("/scrape/{source_id}/direct", response_model=ScrapeResultResponse)
async def scrape_source_direct(
    source_id: str,
    db: Database = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Directly scrape a source without using Celery (for testing/demo).

    Requires authentication.
    """
    from api.db.cosmos_db import CosmosCollections
    from api.db.models import ArticleDocument
    from api.services.scraper import create_scraper
    from datetime import datetime, timedelta

    # Verify source exists
    source = db[CosmosCollections.SOURCES].find_one({"id": source_id})

    if not source:
        raise HTTPException(status_code=404, detail=f"Source not found: {source_id}")

    if not source.get("active", True):
        raise HTTPException(status_code=400, detail=f"Source is inactive: {source_id}")

    try:
        # Create scraper
        scraper = create_scraper(
            source_id=source["id"],
            source_type=source["type"],
            source_url=source.get("url", ""),
            config=source.get("config", {}),
        )

        # Run scraper
        articles = await scraper.scrape()

        # Store articles in database
        stored_count = 0
        duplicate_count = 0

        for article in articles:
            try:
                # Check for duplicates by URL
                existing = db[CosmosCollections.ARTICLES].find_one(
                    {"source_url": article.source_url}
                )

                if existing:
                    duplicate_count += 1
                    continue

                # Store new article
                article_data = article.to_dict()
                article_doc = ArticleDocument.create(
                    source_id=source_id,
                    source_url=article_data["source_url"],
                    title=article_data["title"],
                    **article_data
                )
                db[CosmosCollections.ARTICLES].insert_one(article_doc)
                stored_count += 1

            except Exception as e:
                print(f"Error storing article: {e}")
                continue

        # Update source metadata
        db[CosmosCollections.SOURCES].update_one(
            {"id": source_id},
            {
                "$set": {
                    "last_checked_at": datetime.utcnow(),
                    "next_check_at": datetime.utcnow() + timedelta(
                        hours=source.get("check_interval_hours", 6)
                    ),
                    "last_error": None,
                },
                "$inc": {"success_count": 1},
            }
        )

        return {
            "success": True,
            "message": f"Successfully scraped {source['name']}",
            "articles_scraped": len(articles),
            "articles_stored": stored_count,
            "duplicates_found": duplicate_count,
        }

    except Exception as e:
        # Update source error status
        db[CosmosCollections.SOURCES].update_one(
            {"id": source_id},
            {
                "$set": {
                    "last_error": str(e),
                    "last_checked_at": datetime.utcnow(),
                },
                "$inc": {"failure_count": 1},
            }
        )
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


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
