# Function App RSS Scraping Integration

## Feature Description
This feature integrates the scraping of user-defined RSS feeds directly into the Azure Function App's article discovery process. Previously, the Function App relied solely on user topics and Google Search to find new articles. With this enhancement, the system now actively monitors and scrapes articles from RSS feeds stored in the database, ensuring that users receive updates from their subscribed sources.

## Implementation Details

### Function App (`packages/functions`)
- **File:** `shared/orchestration_logic.py`
  - **`find_new_articles` Function:**
    - **Import `feedparser`:** The `feedparser` library is now imported to handle RSS feed parsing.
    - **Fetch RSS Feeds:** The function now connects to the MongoDB `rss_feeds` collection and retrieves all active RSS feed URLs.
    - **Parse RSS Feeds:** For each retrieved RSS feed URL, `feedparser.parse()` is used to extract individual article entries.
    - **Extract Article Links:** Links from each RSS entry are extracted and added to a set of `all_found_urls`.
    - **Combined Article Discovery:** The links discovered from RSS feeds are combined with the links found through the existing Google Search API (which uses user topics).
    - **Deduplication:** The combined set of URLs is then deduplicated against articles already present in the `articles` collection in the database.
    - **Return New URLs:** A list of unique, new article URLs is returned, which are then queued for further processing (e.g., by `CrawlerWorker`).

## How it Works
1.  The `CrawlerOrchestrator` Azure Function (typically triggered by a timer) invokes the `find_new_articles` logic.
2.  Within `find_new_articles`, the system first queries the database for all stored RSS feed URLs.
3.  It then iterates through these URLs, parsing each RSS feed to extract new article links.
4.  Concurrently (or sequentially, depending on implementation), it continues to perform Google Searches based on user topics to find additional articles.
5.  All discovered article links (from both RSS feeds and Google Search) are collected.
6.  These links are then checked against the `articles` collection to prevent re-processing already stored articles.
7.  Finally, a list of truly new article URLs is generated and passed on to the next stage of the crawling pipeline.
