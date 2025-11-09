#!/usr/bin/env python3
"""Migration script to add titles to existing RSS feeds."""
import feedparser
from dependencies import get_db_client

def migrate_feed_titles():
    """Fetch and update titles for all RSS feeds in the database."""
    db = get_db_client()
    rss_feeds_collection = db.rss_feeds
    
    # Get all feeds without titles
    feeds = list(rss_feeds_collection.find({}))
    print(f"Found {len(feeds)} feeds to process")
    
    updated_count = 0
    for feed in feeds:
        feed_id = feed.get('id')
        url = feed.get('url')
        current_title = feed.get('title')
        
        # Skip if already has a title
        if current_title and current_title != "Untitled Feed":
            print(f"✓ Feed {feed_id} already has title: {current_title}")
            continue
        
        # Fetch the RSS feed to get the title
        feed_title = "Untitled Feed"
        try:
            print(f"Fetching title for: {url}")
            parsed_feed = feedparser.parse(url)
            if parsed_feed.feed and hasattr(parsed_feed.feed, 'title'):
                feed_title = parsed_feed.feed.title
                print(f"  Found title: {feed_title}")
        except Exception as e:
            print(f"  ✗ Failed to fetch feed title: {e}")
            continue
        
        # Update the feed in the database
        rss_feeds_collection.update_one(
            {"id": feed_id},
            {"$set": {"title": feed_title}}
        )
        updated_count += 1
        print(f"  ✓ Updated feed {feed_id}")
    
    print(f"\nMigration complete! Updated {updated_count} feeds.")

if __name__ == "__main__":
    migrate_feed_titles()
