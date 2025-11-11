import os
import pymongo
import feedparser
from datetime import datetime
from langchain_community.utilities import GoogleSearchAPIWrapper
from shared.key_vault_client import get_secret_client
from shared.backend_client import BackendAPIClient
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
        backend_client = BackendAPIClient()

        # --- 2. Process RSS Feeds - Create Articles Directly ---
        logger.info("Processing RSS feeds...")
        rss_articles_created = 0

        for feed_doc in rss_feeds_collection.find({}):
            feed_url = feed_doc.get("url")
            feed_id = feed_doc.get("id")
            feed_title = feed_doc.get("title", "Unknown Feed")

            if not feed_url:
                logger.warning("RSS feed document missing URL", feed_id=feed_id)
                continue

            logger.info("Parsing RSS feed", url=feed_url, feed_id=feed_id)
            try:
                parsed_feed = feedparser.parse(feed_url)

                for entry in parsed_feed.entries:
                    if not hasattr(entry, 'link'):
                        continue

                    # Create article directly from RSS metadata (no crawling needed)
                    article_data = {
                        'title': entry.get('title', 'Untitled'),
                        'link': entry.link,
                        'summary': entry.get('summary', entry.get('description', '')),
                        'published': entry.get('published', datetime.utcnow().isoformat()),
                        'tags': [tag.get('term', '') for tag in entry.get('tags', [])],
                        'source': 'rss',
                        'feed_id': feed_id,
                        'feed_name': feed_title,
                        'content': None  # RSS articles don't need full content initially
                    }

                    try:
                        result = backend_client.create_article(article_data)
                        if 'created successfully' in result.get('message', ''):
                            rss_articles_created += 1
                            logger.debug("Created article from RSS",
                                       article_title=article_data['title'],
                                       feed_name=feed_title)
                    except Exception as e:
                        logger.error("Failed to create article from RSS",
                                   article_link=entry.link,
                                   feed_id=feed_id,
                                   error=str(e))

            except Exception as e:
                logger.error("Error parsing RSS feed", url=feed_url, error=str(e))

        logger.info("Created articles from RSS feeds", count=rss_articles_created)

        # --- 3. Fetch User Topics and Search for Additional Articles ---
        # Google Search results will still need crawling (no RSS metadata available)
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
                        search_results = search.results(f"latest articles about {topic}", num_results=5)
                        for res in search_results:
                            if "link" in res:
                                all_found_urls.add(res["link"])
                    except Exception as e:
                        logger.error("Error during Google Search for topic", topic=topic, error=str(e))

                logger.info("Found URLs from Google Search (for crawling)", count=len(all_found_urls))

        # --- 4. Deduplicate Google Search URLs against existing articles ---
        # (RSS articles were already deduplicated via create_article API)
        if not all_found_urls:
            logger.info("No Google Search URLs to crawl. RSS articles created directly.")
            return []

        existing_links = {article["link"] for article in articles_collection.find({"link": {"$in": list(all_found_urls)}}, {"link": 1})}

        logger.info("Found existing Google Search articles in DB", count=len(existing_links))

        new_urls_to_crawl = list(all_found_urls - existing_links)

        logger.info("Queuing new Google Search URLs for crawling", count=len(new_urls_to_crawl))

        return new_urls_to_crawl

    except Exception as e:
        logger.error("An unexpected error occurred in orchestration logic", error=str(e))
        return []
