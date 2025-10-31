"""Synchronous scraping functions (without Celery) for API endpoints."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List
import uuid
import yaml
from pathlib import Path

from api.db.cosmos_db import get_cosmos_client, CosmosCollections
from api.services.scraper import create_scraper

logger = logging.getLogger(__name__)


def load_sources_from_yaml() -> List[Dict]:
    """Load sources from YAML configuration file.

    Returns:
        List of source dictionaries
    """
    config_file = Path(__file__).parent.parent.parent / "config" / "sources.yaml"

    with open(config_file, "r") as f:
        data = yaml.safe_load(f)
        sources = data.get("sources", [])

    logger.info(f"Loaded {len(sources)} sources from configuration")
    return sources


def sync_sources_to_db() -> dict:
    """
    Sync sources from YAML config to database.

    Returns:
        dict with sync results
    """
    logger.info("Syncing sources from YAML to database")

    try:
        # Load sources from YAML
        sources = load_sources_from_yaml()
        logger.info(f"Loaded {len(sources)} sources from YAML")

        # Get database
        cosmos = get_cosmos_client()
        sources_collection = cosmos.get_collection(CosmosCollections.SOURCES)

        # Sync each source
        synced_count = 0
        updated_count = 0

        for source_data in sources:
            source_id = source_data.get("id")

            # Check if source exists
            existing = sources_collection.find_one({"id": source_id})

            # Add metadata
            now = datetime.utcnow()
            source_data["last_sync_at"] = now

            if existing:
                # Update existing source
                sources_collection.update_one(
                    {"id": source_id},
                    {"$set": source_data}
                )
                updated_count += 1
                logger.debug(f"Updated source: {source_id}")
            else:
                # Insert new source
                source_data["created_at"] = now
                sources_collection.insert_one(source_data)
                synced_count += 1
                logger.debug(f"Created source: {source_id}")

        result = {
            "success": True,
            "message": f"Synced {len(sources)} sources ({synced_count} new, {updated_count} updated)",
            "sources_synced": synced_count,
            "sources_updated": updated_count,
            "total_sources": len(sources)
        }

        logger.info(result["message"])
        return result

    except Exception as e:
        logger.error(f"Error syncing sources: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to sync sources"
        }


async def scrape_source_sync(source_id: str) -> dict:
    """
    Scrape content from a single source (async for FastAPI).

    Args:
        source_id: Source identifier

    Returns:
        dict with scraping results
    """
    logger.info(f"Starting scrape for source: {source_id}")

    try:
        # Get database
        cosmos = get_cosmos_client()
        sources_collection = cosmos.get_collection(CosmosCollections.SOURCES)
        articles_collection = cosmos.get_collection(CosmosCollections.ARTICLES)

        # Get source from database
        source_record = sources_collection.find_one({"id": source_id})

        if not source_record:
            logger.error(f"Source not found: {source_id}")
            return {
                "success": False,
                "error": "Source not found",
                "articles_scraped": 0,
                "articles_stored": 0
            }

        if not source_record.get("active", True):
            logger.info(f"Source is inactive: {source_id}")
            return {
                "success": False,
                "error": "Source inactive",
                "articles_scraped": 0,
                "articles_stored": 0
            }

        # Create scraper
        scraper = create_scraper(
            source_id=source_record["id"],
            source_type=source_record["type"],
            source_url=source_record.get("url", ""),
            config=source_record.get("config", {}),
        )

        # Run scraper (use await since we're in async context)
        articles = await scraper.scrape()

        logger.info(f"Scraped {len(articles)} articles from {source_id}")

        # Store articles in database
        stored_count = 0
        duplicate_count = 0

        for article in articles:
            try:
                # Check for duplicates by URL
                existing = articles_collection.find_one(
                    {"source_url": article.source_url}
                )

                if existing:
                    duplicate_count += 1
                    logger.debug(f"Duplicate article skipped: {article.source_url}")
                    continue

                # Create article document
                article_doc = {
                    "id": str(uuid.uuid4()),
                    "source_id": source_id,
                    "title": article.title,
                    "source_url": article.source_url,
                    "content": article.content,
                    "published_at": article.published_at,
                    "fetched_at": datetime.utcnow(),
                    "processing_status": "pending",
                    "companies": [],
                    "industries": [],
                }

                articles_collection.insert_one(article_doc)
                stored_count += 1
                logger.debug(f"Stored article: {article.title}")

            except Exception as e:
                logger.error(f"Error storing article: {e}")
                continue

        # Update source last_checked_at
        sources_collection.update_one(
            {"id": source_id},
            {
                "$set": {
                    "last_checked_at": datetime.utcnow(),
                    "success_count": source_record.get("success_count", 0) + 1
                }
            }
        )

        result = {
            "success": True,
            "message": f"Scraped {stored_count} new articles from {source_id}",
            "articles_scraped": len(articles),
            "articles_stored": stored_count,
            "duplicates_found": duplicate_count
        }

        logger.info(result["message"])
        return result

    except Exception as e:
        logger.error(f"Error scraping source {source_id}: {e}", exc_info=True)

        # Update source failure count
        try:
            cosmos = get_cosmos_client()
            sources_collection = cosmos.get_collection(CosmosCollections.SOURCES)
            source_record = sources_collection.find_one({"id": source_id})
            if source_record:
                sources_collection.update_one(
                    {"id": source_id},
                    {
                        "$set": {
                            "last_checked_at": datetime.utcnow(),
                            "failure_count": source_record.get("failure_count", 0) + 1
                        }
                    }
                )
        except:
            pass

        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to scrape {source_id}",
            "articles_scraped": 0,
            "articles_stored": 0
        }
