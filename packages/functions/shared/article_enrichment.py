"""
Utility functions for enriching articles with metadata for newsletters.
"""
from datetime import datetime, timezone
import re


def calculate_read_time(text: str) -> str:
    """
    Calculate estimated reading time based on word count.

    Args:
        text: Article text or summary

    Returns:
        Formatted read time string like "5 min" or "1 min"
    """
    # Average reading speed: 200-250 words per minute
    # We'll use 225 as middle ground
    words_per_minute = 225

    # Count words (split by whitespace)
    word_count = len(text.split())

    # Calculate minutes
    minutes = max(1, round(word_count / words_per_minute))

    return f"{minutes} min"


def get_relative_time(published_date: datetime) -> str:
    """
    Get human-readable relative time from a datetime.

    Args:
        published_date: DateTime when article was published

    Returns:
        Relative time string like "2h ago", "1d ago", "just now"
    """
    if not published_date:
        return ""

    # Ensure timezone awareness
    if published_date.tzinfo is None:
        published_date = published_date.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    diff = now - published_date

    seconds = diff.total_seconds()

    # Less than a minute
    if seconds < 60:
        return "just now"

    # Less than an hour
    minutes = int(seconds / 60)
    if minutes < 60:
        return f"{minutes}m ago"

    # Less than a day
    hours = int(minutes / 60)
    if hours < 24:
        return f"{hours}h ago"

    # Less than a week
    days = int(hours / 24)
    if days < 7:
        return f"{days}d ago"

    # Less than a month
    weeks = int(days / 7)
    if weeks < 4:
        return f"{weeks}w ago"

    # Months
    months = int(days / 30)
    if months < 12:
        return f"{months}mo ago"

    # Years
    years = int(days / 365)
    return f"{years}y ago"


def match_article_to_topics(article: dict, user_topics: list[str]) -> str:
    """
    Match an article to the most relevant user topic.

    Args:
        article: Article dict with 'title', 'summary', etc.
        user_topics: List of user's topic preferences

    Returns:
        Best matching topic or empty string
    """
    # Topic keyword mapping (lowercase for matching)
    topic_keywords = {
        'technology': ['tech', 'software', 'ai', 'artificial intelligence', 'computer', 'digital', 'internet', 'app', 'startup', 'innovation', 'data', 'coding', 'programming', 'cybersecurity'],
        'business': ['business', 'economy', 'market', 'stock', 'finance', 'company', 'corporate', 'entrepreneur', 'investment', 'trade', 'commerce'],
        'science': ['science', 'research', 'study', 'discovery', 'scientist', 'experiment', 'laboratory', 'physics', 'chemistry', 'biology'],
        'health': ['health', 'medical', 'doctor', 'medicine', 'hospital', 'disease', 'wellness', 'fitness', 'nutrition', 'mental health', 'therapy'],
        'sports': ['sport', 'game', 'player', 'team', 'championship', 'olympic', 'football', 'basketball', 'soccer', 'tennis', 'athlete'],
        'entertainment': ['movie', 'film', 'music', 'celebrity', 'actor', 'singer', 'concert', 'album', 'show', 'television', 'streaming'],
        'politics': ['politic', 'government', 'election', 'president', 'congress', 'senate', 'policy', 'vote', 'law', 'minister', 'parliament'],
        'world': ['world', 'international', 'global', 'country', 'nation', 'foreign', 'diplomatic', 'crisis', 'conflict'],
        'environment': ['environment', 'climate', 'carbon', 'emission', 'sustainability', 'renewable', 'conservation', 'pollution', 'ecosystem'],
        'education': ['education', 'school', 'university', 'student', 'teacher', 'learning', 'college', 'academic', 'curriculum'],
        'travel': ['travel', 'tourism', 'destination', 'hotel', 'flight', 'vacation', 'trip', 'adventure', 'tourist'],
        'food': ['food', 'restaurant', 'recipe', 'chef', 'cooking', 'cuisine', 'dish', 'dining', 'meal', 'culinary']
    }

    # Get article text to search
    article_text = (
        article.get('title', '') + ' ' +
        article.get('summary', '') + ' ' +
        article.get('description', '')
    ).lower()

    # Score each topic
    topic_scores = {}
    for topic in user_topics:
        topic_lower = topic.lower()
        keywords = topic_keywords.get(topic_lower, [topic_lower])

        score = 0
        for keyword in keywords:
            # Count occurrences of this keyword
            score += article_text.count(keyword)

        if score > 0:
            topic_scores[topic] = score

    # Return topic with highest score
    if topic_scores:
        return max(topic_scores, key=topic_scores.get)

    return ""


def extract_source_from_url(url: str) -> str:
    """
    Extract a clean source name from an article URL.

    Args:
        url: Article URL

    Returns:
        Source name like "TechCrunch", "Reuters", etc.
    """
    if not url:
        return ""

    # Extract domain
    match = re.search(r'https?://(?:www\.)?([^/]+)', url)
    if not match:
        return ""

    domain = match.group(1)

    # Remove common TLDs and get main name
    domain = re.sub(r'\.(com|org|net|co\.uk|io|ai)$', '', domain)

    # Capitalize properly
    # Handle special cases
    special_cases = {
        'techcrunch': 'TechCrunch',
        'nytimes': 'The New York Times',
        'wsj': 'The Wall Street Journal',
        'bbc': 'BBC',
        'cnn': 'CNN',
        'reuters': 'Reuters',
        'theguardian': 'The Guardian',
        'forbes': 'Forbes',
        'bloomberg': 'Bloomberg',
        'wired': 'WIRED',
        'arstechnica': 'Ars Technica',
        'theverge': 'The Verge',
    }

    domain_lower = domain.lower()
    if domain_lower in special_cases:
        return special_cases[domain_lower]

    # Default: capitalize first letter of each word
    return ' '.join(word.capitalize() for word in domain.split('.'))


def enrich_article(article: dict, user_topics: list[str] = None) -> dict:
    """
    Enrich an article with all metadata needed for the email template.

    Args:
        article: Article dict with basic fields
        user_topics: User's topic preferences for matching

    Returns:
        Enriched article dict with all metadata fields
    """
    enriched = article.copy()

    # Add source if not present
    if 'source' not in enriched or not enriched['source']:
        url = enriched.get('link') or enriched.get('url', '')
        enriched['source'] = extract_source_from_url(url)

    # Add read time if not present
    if 'read_time' not in enriched or not enriched['read_time']:
        text = enriched.get('summary', '') or enriched.get('description', '')
        enriched['read_time'] = calculate_read_time(text)

    # Add relative time if not present
    if 'published_time_ago' not in enriched or not enriched['published_time_ago']:
        created_at = enriched.get('created_at')
        if created_at:
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except:
                    created_at = None

            if created_at:
                enriched['published_time_ago'] = get_relative_time(created_at)

    # Match to topic if not present
    if user_topics and ('topic' not in enriched or not enriched['topic']):
        enriched['topic'] = match_article_to_topics(enriched, user_topics)

    return enriched


def enrich_articles(articles: list[dict], user_topics: list[str] = None) -> list[dict]:
    """
    Enrich a list of articles with metadata.

    Args:
        articles: List of article dicts
        user_topics: User's topic preferences

    Returns:
        List of enriched article dicts
    """
    return [enrich_article(article, user_topics) for article in articles]
