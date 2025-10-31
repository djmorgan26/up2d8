"""Celery tasks for content scraping."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List

from celery import Task

from workers.celery_app import celery_app
from api.db.session import get_db
from api.db.cosmos_db import CosmosCollections
from api.db.models import ArticleDocument, SourceDocument
from api.services.scraper import create_scraper, SourceManager, ScrapedArticle

logger = logging.getLogger(__name__)


class CallbackTask(Task):
    """Base task with callbacks for success/failure."""

    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds."""
        logger.info(f"Task {task_id} succeeded")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails."""
        logger.error(f"Task {task_id} failed: {exc}", exc_info=einfo)


# ============================================================================
# Scraping Tasks
# ============================================================================


@celery_app.task(
    base=CallbackTask,
    bind=True,
    name="workers.tasks.scraping.scrape_source",
    max_retries=3,
    default_retry_delay=60,
)
def scrape_source(self, source_id: str) -> dict:
    """Scrape content from a single source.

    Args:
        source_id: Source identifier

    Returns:
        dict with scraping results
    """
    logger.info(f"Starting scrape task for source: {source_id}")

    try:
        # Get database
        db = get_db()

        # Get source from database
        source_record = db[CosmosCollections.SOURCES].find_one({"id": source_id})

        if not source_record:
            logger.error(f"Source not found: {source_id}")
            return {"success": False, "error": "Source not found", "articles_count": 0}

        if not source_record.get("active", True):
            logger.info(f"Source is inactive: {source_id}")
            return {"success": False, "error": "Source inactive", "articles_count": 0}

        # Create scraper
        scraper = create_scraper(
            source_id=source_record["id"],
            source_type=source_record["type"],
            source_url=source_record.get("url", ""),
            config=source_record.get("config", {}),
        )

        # Run scraper (handle async)
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        articles = loop.run_until_complete(scraper.scrape())

        logger.info(f"Scraped {len(articles)} articles from {source_id}")

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
                    logger.debug(f"Duplicate article skipped: {article.source_url}")
                    continue

                # Check for duplicates by content hash
                existing_hash = db[CosmosCollections.ARTICLES].find_one(
                    {"content_hash": article.content_hash}
                )

                if existing_hash:
                    # Mark as duplicate
                    article_data = article.to_dict()
                    article_data["duplicate_of"] = existing_hash["id"]
                    article_data["canonical"] = False
                    article_doc = ArticleDocument.create(
                        source_id=source_id,
                        source_url=article_data["source_url"],
                        title=article_data["title"],
                        **article_data
                    )
                    db[CosmosCollections.ARTICLES].insert_one(article_doc)
                    duplicate_count += 1
                else:
                    # New article
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
                logger.error(f"Error storing article: {e}", exc_info=True)
                continue

        # Update source metadata
        db[CosmosCollections.SOURCES].update_one(
            {"id": source_id},
            {
                "$set": {
                    "last_checked_at": datetime.utcnow(),
                    "next_check_at": datetime.utcnow() + timedelta(
                        hours=source_record.get("check_interval_hours", 6)
                    ),
                    "last_error": None,
                },
                "$inc": {"success_count": 1},
            }
        )

        result = {
            "success": True,
            "source_id": source_id,
            "articles_scraped": len(articles),
            "articles_stored": stored_count,
            "duplicates_found": duplicate_count,
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info(f"Scrape task completed for {source_id}: {result}")
        return result

    except Exception as exc:
        logger.error(f"Error scraping source {source_id}: {exc}", exc_info=True)

        # Update source error status
        try:
            db = get_db()
            db[CosmosCollections.SOURCES].update_one(
                {"id": source_id},
                {
                    "$set": {
                        "last_error": str(exc),
                        "last_checked_at": datetime.utcnow(),
                    },
                    "$inc": {"failure_count": 1},
                }
            )
        except Exception as db_err:
            logger.error(f"Error updating source error status: {db_err}")

        # Retry task
        raise self.retry(exc=exc)


@celery_app.task(
    base=CallbackTask,
    name="workers.tasks.scraping.scrape_priority_sources",
)
def scrape_priority_sources(priority: str = "high") -> dict:
    """Scrape all sources of a given priority level.

    Args:
        priority: Priority level (high, medium, low)

    Returns:
        dict with overall results
    """
    logger.info(f"Starting batch scrape for {priority} priority sources")

    try:
        # Load source manager
        manager = SourceManager()
        sources = manager.get_sources_by_priority(priority)

        logger.info(f"Found {len(sources)} {priority} priority sources")

        # Get database
        db = get_db()

        # Dispatch individual scrape tasks
        results = []
        for source in sources:
            try:
                # Check if source needs scraping (based on last_checked_at)
                source_record = db[CosmosCollections.SOURCES].find_one(
                    {"id": source["id"]}
                )

                if source_record:
                    # Check if it's time to scrape
                    next_check_at = source_record.get("next_check_at")
                    if next_check_at and next_check_at > datetime.utcnow():
                        logger.debug(
                            f"Skipping {source['id']}, next check at {next_check_at}"
                        )
                        continue

                # Dispatch scrape task
                task_result = scrape_source.delay(source["id"])
                results.append(
                    {"source_id": source["id"], "task_id": task_result.id}
                )

            except Exception as e:
                logger.error(f"Error dispatching scrape for {source['id']}: {e}")
                continue

        return {
            "success": True,
            "priority": priority,
            "tasks_dispatched": len(results),
            "tasks": results,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error in batch scrape for {priority} sources: {e}", exc_info=True)
        return {
            "success": False,
            "priority": priority,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@celery_app.task(
    base=CallbackTask,
    name="workers.tasks.scraping.scrape_all_sources",
)
def scrape_all_sources() -> dict:
    """Scrape all active sources (manual trigger).

    Returns:
        dict with overall results
    """
    logger.info("Starting scrape for all active sources")

    try:
        manager = SourceManager()
        sources = manager.get_active_sources()

        logger.info(f"Found {len(sources)} active sources")

        # Dispatch tasks for all sources
        results = []
        for source in sources:
            try:
                task_result = scrape_source.delay(source["id"])
                results.append(
                    {"source_id": source["id"], "task_id": task_result.id}
                )
            except Exception as e:
                logger.error(f"Error dispatching scrape for {source['id']}: {e}")
                continue

        return {
            "success": True,
            "total_sources": len(sources),
            "tasks_dispatched": len(results),
            "tasks": results,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error in scrape_all_sources: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


# ============================================================================
# Source Management Tasks
# ============================================================================


@celery_app.task(
    base=CallbackTask,
    name="workers.tasks.scraping.sync_sources_to_db",
)
def sync_sources_to_db() -> dict:
    """Sync source configurations from YAML to database.

    Returns:
        dict with sync results
    """
    logger.info("Syncing sources from config to database")

    try:
        # Load sources from YAML
        manager = SourceManager()
        yaml_sources = manager.sources

        # Get database
        db = get_db()

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
                logger.error(f"Error syncing source {source_config['id']}: {e}")
                continue

        result = {
            "success": True,
            "sources_created": created_count,
            "sources_updated": updated_count,
            "total_sources": len(yaml_sources),
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info(f"Source sync completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Error syncing sources to database: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
