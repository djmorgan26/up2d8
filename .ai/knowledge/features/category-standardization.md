# Category Standardization for RSS Feeds

## Feature Description
This feature introduces a robust mechanism for standardizing categories assigned to RSS feeds. This prevents the proliferation of similar or redundant categories (e.g., "Technology" vs. "Tech News") and ensures consistency across the application. Categories are standardized both when new feeds are added (including AI-suggested feeds) and for existing feeds in the database.

## Implementation Details

### Backend (`packages/backend-api`)
- **File:** `api/rss_feeds.py`
  - **`STANDARD_CATEGORIES` Dictionary:** A dictionary defining a set of standard categories (e.g., "Technology", "News") and their associated synonyms (e.g., "tech news", "innovation" for "Technology"). The keys of this dictionary are the desired regular capitalized standard category names.
  - **`standardize_category(raw_category: str | None) -> str` Function:**
    - Takes a raw category string as input.
    - Cleans and normalizes the input (strips whitespace, converts to lowercase).
    - Iterates through `STANDARD_CATEGORIES` to find a match based on the cleaned category or its synonyms.
    - Returns the corresponding standard category name (e.g., "Technology") if a match is found.
    - Returns "Uncategorized" if the input is `None` or empty.
    - Returns the original cleaned category if no standard match is found.
  - **`create_rss_feed` Function:**
    - The `feed.category` (received from the frontend or LLM) is passed through the `standardize_category` function before being saved to the database.
  - **`RssFeedCreate` Model:** Updated to include an optional `title: str | None = None` field, allowing the frontend to pass a title directly. The `create_rss_feed` function prioritizes this title over fetching it via `feedparser`.

### Database Standardization Script (`standardize_feeds_script.py`)
- A temporary Python script was created to apply the `standardize_category` function to all existing RSS feeds in the MongoDB database.
- It iterates through the `rss_feeds` collection, standardizes each feed's category, and updates the database if the category changes. This ensures that historical data aligns with the new standardization rules.

## How it Works
1.  When a new RSS feed is added (either manually or via AI suggestion), its proposed category is passed to the `standardize_category` function in the backend.
2.  The function attempts to map the proposed category to one of the predefined `STANDARD_CATEGORIES` using its list of synonyms.
3.  The standardized category is then saved to the database.
4.  A one-time script was executed to update all previously existing feeds in the database to conform to these new standardization rules.
5.  The frontend now displays and uses these standardized categories, ensuring a consistent user experience.
