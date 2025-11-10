import os
import pymongo
import feedparser
from langchain_community.utilities import GoogleSearchAPIWrapper
from shared.key_vault_client import get_secret_client
from shared.retry_utils import retry_with_backoff
import structlog

logger = structlog.get_logger()

def find_new_articles() -> list[str]:
    """
    Core orchestration logic to find new articles based on user topics and RSS feeds.
    This function is designed to be called by different triggers.
    """
    try:
        # --- 1. Configuration and Database Connection ---
        secret_client = get_secret_client()
        
        cosmos_db_connection_string = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value
        google_api_key = secret_client.get_secret("GOOGLE-CUSTOM-SEARCH-API").value
        google_cse_id = os.getenv("GOOGLE_CSE_ID")

        # Initialize MongoDB client
        client = pymongo.MongoClient(cosmos_db_connection_string)
        db = client.up2d8
        users_collection = db.users
        articles_collection = db.articles
        rss_feeds_collection = db.rss_feeds # Get RSS feeds collection

        all_found_urls = set()

        # --- 2. Process RSS Feeds ---
        logger.info("Processing RSS feeds...")
        for feed_doc in rss_feeds_collection.find({}):
            feed_url = feed_doc.get("url")
            if not feed_url:
                logger.warning("RSS feed document missing URL", feed_id=feed_doc.get("id"))
                continue
            
            logger.info("Parsing RSS feed", url=feed_url)
            try:
                # Parse RSS feed with retry logic for network failures
                @retry_with_backoff(max_attempts=3, base_delay=1.0, max_delay=10.0)
                def _parse_feed_with_retry():
                    return feedparser.parse(feed_url)

                parsed_feed = _parse_feed_with_retry()
                for entry in parsed_feed.entries:
                    if hasattr(entry, 'link'):
                        all_found_urls.add(entry.link)
            except Exception as e:
                logger.error("Error parsing RSS feed", url=feed_url, error=str(e))
        
        logger.info("Found URLs from RSS feeds", count=len(all_found_urls))

        # --- 3. Fetch User Topics and Search (Existing Logic) ---
        all_topics = set()
        for user in users_collection.find({}, {"topics": 1}):
            for topic in user.get("topics", []):
                all_topics.add(topic)
        
        if not all_topics:
            logger.warning("No user topics found for Google Search.")
        else:
            logger.info("Found unique user topics", topics=list(all_topics))

            if not google_cse_id:
                logger.warning("GOOGLE_CSE_ID is not set. Google Search will not run.")
            else:
                os.environ["GOOGLE_API_KEY"] = google_api_key
                os.environ["GOOGLE_CSE_ID"] = google_cse_id

                search = GoogleSearchAPIWrapper()

                for topic in all_topics:
                    logger.info("Searching for articles via Google Search", topic=topic)
                    try:
                        # Google Search with retry logic for API rate limits
                        @retry_with_backoff(max_attempts=3, base_delay=2.0, max_delay=30.0)
                        def _search_with_retry():
                            return search.results(f"latest articles about {topic}", num_results=5)

                        search_results = _search_with_retry()
                        for res in search_results:
                            if "link" in res:
                                all_found_urls.add(res["link"])
                    except Exception as e:
                        logger.error("Error during Google Search for topic", topic=topic, error=str(e))
                
                logger.info("Found total URLs from RSS and Google Search", count=len(all_found_urls))

        if not all_found_urls:
            logger.warning("No URLs found from RSS feeds or Google Search. Orchestrator finished.")
            return []
        
        # --- 4. Deduplicate against existing articles ---
        existing_links = {article["link"] for article in articles_collection.find({"link": {"$in": list(all_found_urls)}}, {"link": 1})}
        
        logger.info("Found existing articles in DB", count=len(existing_links))

        new_urls_to_crawl = list(all_found_urls - existing_links)

        logger.info("Queuing new URLs for crawling", count=len(new_urls_to_crawl))

        return new_urls_to_crawl

    except Exception as e:
        logger.error("An unexpected error occurred in orchestration logic", error=str(e))
        return []
