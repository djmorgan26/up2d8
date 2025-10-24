"""Content scraping service for UP2D8.

Provides base classes and implementations for scraping content from various sources:
- RSS feeds
- Web scraping
- GitHub API
- News APIs
"""

import asyncio
import hashlib
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

import feedparser
import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page

logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================


class ScrapedArticle:
    """Data class for scraped article content."""

    def __init__(
        self,
        source_id: str,
        source_url: str,
        title: str,
        content: Optional[str] = None,
        content_html: Optional[str] = None,
        author: Optional[str] = None,
        published_at: Optional[datetime] = None,
        companies: Optional[List[str]] = None,
        industries: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.source_id = source_id
        self.source_url = source_url
        self.title = title
        self.content = content
        self.content_html = content_html
        self.author = author
        self.published_at = published_at or datetime.utcnow()
        self.companies = companies or []
        self.industries = industries or []
        self.metadata = metadata or {}

        # Generate content hash for deduplication
        self.content_hash = self._generate_hash()

    def _generate_hash(self) -> str:
        """Generate SHA-256 hash of content for deduplication."""
        content_str = f"{self.title}{self.content or ''}"
        return hashlib.sha256(content_str.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            "source_id": self.source_id,
            "source_url": self.source_url,
            "source_type": self.metadata.get("source_type", "unknown"),
            "title": self.title,
            "content": self.content,
            "content_html": self.content_html,
            "author": self.author,
            "published_at": self.published_at,
            "companies": self.companies,
            "industries": self.industries,
            "content_hash": self.content_hash,
            "extra_metadata": self.metadata,
            "processing_status": "pending",
            "fetched_at": datetime.utcnow(),
        }


# ============================================================================
# Base Scraper
# ============================================================================


class BaseScraper(ABC):
    """Abstract base class for all scrapers."""

    def __init__(
        self,
        source_id: str,
        source_url: str,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.source_id = source_id
        self.source_url = source_url
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # HTTP client configuration
        self.timeout = self.config.get("timeout_seconds", 30)
        self.retry_attempts = self.config.get("retry_attempts", 3)
        self.user_agent = self.config.get(
            "user_agent", "UP2D8Bot/1.0 (+https://up2d8.ai/bot)"
        )

    @abstractmethod
    async def scrape(self) -> List[ScrapedArticle]:
        """Scrape articles from the source.

        Returns:
            List of ScrapedArticle objects
        """
        pass

    async def _fetch_url(
        self, url: str, headers: Optional[Dict[str, str]] = None
    ) -> str:
        """Fetch URL content with retry logic.

        Args:
            url: URL to fetch
            headers: Optional HTTP headers

        Returns:
            Response text

        Raises:
            httpx.HTTPError: If request fails after all retries
        """
        default_headers = {"User-Agent": self.user_agent}
        if headers:
            default_headers.update(headers)

        for attempt in range(self.retry_attempts):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        url, headers=default_headers, timeout=self.timeout, follow_redirects=True
                    )
                    response.raise_for_status()
                    return response.text
            except httpx.HTTPError as e:
                self.logger.warning(
                    f"Attempt {attempt + 1}/{self.retry_attempts} failed for {url}: {e}"
                )
                if attempt == self.retry_attempts - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    def _normalize_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime.

        Args:
            date_str: Date string in various formats

        Returns:
            datetime object or None if parsing fails
        """
        if not date_str:
            return None

        # Try common date formats
        import dateparser

        parsed = dateparser.parse(date_str)
        if parsed:
            return parsed

        self.logger.warning(f"Failed to parse date: {date_str}")
        return None


# ============================================================================
# RSS Feed Scraper
# ============================================================================


class RSSFeedScraper(BaseScraper):
    """Scraper for RSS/Atom feeds."""

    async def scrape(self) -> List[ScrapedArticle]:
        """Scrape articles from RSS feed.

        Returns:
            List of ScrapedArticle objects
        """
        self.logger.info(f"Scraping RSS feed: {self.source_url}")

        try:
            # Fetch feed content
            content = await self._fetch_url(self.source_url)

            # Parse RSS/Atom feed
            feed = feedparser.parse(content)

            if feed.get("bozo", False) and feed.get("bozo_exception"):
                self.logger.warning(
                    f"Feed parsing warning for {self.source_url}: {feed.bozo_exception}"
                )

            articles = []
            for entry in feed.entries:
                try:
                    article = self._parse_feed_entry(entry)
                    articles.append(article)
                except Exception as e:
                    self.logger.error(f"Error parsing feed entry: {e}", exc_info=True)
                    continue

            self.logger.info(
                f"Successfully scraped {len(articles)} articles from {self.source_url}"
            )
            return articles

        except Exception as e:
            self.logger.error(f"Error scraping RSS feed {self.source_url}: {e}", exc_info=True)
            raise

    def _parse_feed_entry(self, entry) -> ScrapedArticle:
        """Parse a single feed entry.

        Args:
            entry: feedparser entry object

        Returns:
            ScrapedArticle object
        """
        # Extract title
        title = entry.get("title", "No Title")

        # Extract URL
        source_url = entry.get("link", "")

        # Extract content (try multiple fields)
        content = None
        content_html = None

        if hasattr(entry, "content") and entry.content:
            content_html = entry.content[0].get("value", "")
            content = self._html_to_text(content_html)
        elif hasattr(entry, "summary"):
            content_html = entry.summary
            content = self._html_to_text(entry.summary)
        elif hasattr(entry, "description"):
            content_html = entry.description
            content = self._html_to_text(entry.description)

        # Extract author
        author = entry.get("author", None)

        # Extract published date
        published_at = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            import time

            published_at = datetime.fromtimestamp(time.mktime(entry.published_parsed))
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            import time

            published_at = datetime.fromtimestamp(time.mktime(entry.updated_parsed))

        return ScrapedArticle(
            source_id=self.source_id,
            source_url=source_url,
            title=title,
            content=content,
            content_html=content_html,
            author=author,
            published_at=published_at,
            companies=self.config.get("companies", []),
            industries=self.config.get("industries", []),
            metadata={
                "source_type": "rss",
                "entry_id": entry.get("id", ""),
                "tags": [tag.get("term") for tag in entry.get("tags", [])],
            },
        )

    def _html_to_text(self, html: str) -> str:
        """Convert HTML to plain text.

        Args:
            html: HTML string

        Returns:
            Plain text string
        """
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator=" ", strip=True)


# ============================================================================
# Web Scraper (using Playwright for JavaScript-rendered pages)
# ============================================================================


class WebScraper(BaseScraper):
    """Scraper for websites using Playwright."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selectors = self.config.get("selectors", {})

    async def scrape(self) -> List[ScrapedArticle]:
        """Scrape articles from website.

        Returns:
            List of ScrapedArticle objects
        """
        self.logger.info(f"Scraping website: {self.source_url}")

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                try:
                    # Navigate to URL
                    await page.goto(self.source_url, wait_until="networkidle", timeout=self.timeout * 1000)

                    # Wait for articles to load
                    article_selector = self.selectors.get("article", "article")
                    await page.wait_for_selector(article_selector, timeout=10000)

                    # Extract articles
                    articles = await self._extract_articles(page)

                    return articles

                finally:
                    await browser.close()

        except Exception as e:
            self.logger.error(f"Error scraping website {self.source_url}: {e}", exc_info=True)
            raise

    async def _extract_articles(self, page: Page) -> List[ScrapedArticle]:
        """Extract articles from page using selectors.

        Args:
            page: Playwright page object

        Returns:
            List of ScrapedArticle objects
        """
        articles = []

        # Get all article elements
        article_selector = self.selectors.get("article", "article")
        article_elements = await page.query_selector_all(article_selector)

        self.logger.info(f"Found {len(article_elements)} articles on page")

        for element in article_elements:
            try:
                # Extract title
                title_selector = self.selectors.get("title", "h2, h3")
                title_element = await element.query_selector(title_selector)
                title = await title_element.inner_text() if title_element else "No Title"

                # Extract link
                link_selector = self.selectors.get("link", "a")
                link_element = await element.query_selector(link_selector)
                if link_element:
                    source_url = await link_element.get_attribute("href")
                    # Make absolute URL if relative
                    if source_url and not source_url.startswith("http"):
                        parsed = urlparse(self.source_url)
                        source_url = f"{parsed.scheme}://{parsed.netloc}{source_url}"
                else:
                    source_url = self.source_url

                # Extract summary/content
                summary_selector = self.selectors.get("summary", ".excerpt, p")
                summary_element = await element.query_selector(summary_selector)
                content = await summary_element.inner_text() if summary_element else None

                # Extract date
                date_selector = self.selectors.get("date", "time, .date")
                date_element = await element.query_selector(date_selector)
                date_str = await date_element.inner_text() if date_element else None
                published_at = self._normalize_date(date_str)

                article = ScrapedArticle(
                    source_id=self.source_id,
                    source_url=source_url,
                    title=title.strip(),
                    content=content.strip() if content else None,
                    published_at=published_at,
                    companies=self.config.get("companies", []),
                    industries=self.config.get("industries", []),
                    metadata={"source_type": "scrape"},
                )

                articles.append(article)

            except Exception as e:
                self.logger.warning(f"Error extracting article element: {e}")
                continue

        self.logger.info(f"Successfully extracted {len(articles)} articles")
        return articles


# ============================================================================
# GitHub Scraper
# ============================================================================


class GitHubScraper(BaseScraper):
    """Scraper for GitHub releases and commits."""

    async def scrape(self) -> List[ScrapedArticle]:
        """Scrape GitHub releases.

        Returns:
            List of ScrapedArticle objects
        """
        repo = self.config.get("repo")
        if not repo:
            raise ValueError("GitHub scraper requires 'repo' in config")

        self.logger.info(f"Scraping GitHub repo: {repo}")

        try:
            articles = []

            # Scrape releases
            if "release" in self.config.get("events", ["release"]):
                releases = await self._fetch_releases(repo)
                articles.extend(releases)

            self.logger.info(
                f"Successfully scraped {len(articles)} items from GitHub {repo}"
            )
            return articles

        except Exception as e:
            self.logger.error(f"Error scraping GitHub {repo}: {e}", exc_info=True)
            raise

    async def _fetch_releases(self, repo: str) -> List[ScrapedArticle]:
        """Fetch latest releases from GitHub.

        Args:
            repo: Repository in format 'owner/repo'

        Returns:
            List of ScrapedArticle objects
        """
        url = f"https://api.github.com/repos/{repo}/releases"

        # Add GitHub token if available
        headers = {}
        import os

        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            headers["Authorization"] = f"token {github_token}"

        try:
            content = await self._fetch_url(url, headers=headers)
            import json

            releases_data = json.loads(content)

            articles = []
            for release in releases_data[:5]:  # Get last 5 releases
                article = ScrapedArticle(
                    source_id=self.source_id,
                    source_url=release["html_url"],
                    title=f"{repo} Release: {release['name'] or release['tag_name']}",
                    content=release.get("body", ""),
                    author=release["author"]["login"],
                    published_at=self._normalize_date(release["published_at"]),
                    companies=self.config.get("companies", []),
                    industries=self.config.get("industries", []),
                    metadata={
                        "source_type": "github",
                        "release_tag": release["tag_name"],
                        "prerelease": release.get("prerelease", False),
                    },
                )
                articles.append(article)

            return articles

        except Exception as e:
            self.logger.error(f"Error fetching GitHub releases for {repo}: {e}")
            return []


# ============================================================================
# Scraper Factory
# ============================================================================


def create_scraper(
    source_id: str,
    source_type: str,
    source_url: str,
    config: Optional[Dict[str, Any]] = None,
) -> BaseScraper:
    """Factory function to create appropriate scraper.

    Args:
        source_id: Unique identifier for the source
        source_type: Type of source (rss, scrape, github, api)
        source_url: URL to scrape
        config: Optional configuration dictionary

    Returns:
        Appropriate scraper instance

    Raises:
        ValueError: If source_type is not supported
    """
    scrapers = {
        "rss": RSSFeedScraper,
        "scrape": WebScraper,
        "github": GitHubScraper,
    }

    scraper_class = scrapers.get(source_type)
    if not scraper_class:
        raise ValueError(f"Unsupported source type: {source_type}")

    return scraper_class(source_id=source_id, source_url=source_url, config=config)


# ============================================================================
# Source Manager
# ============================================================================


class SourceManager:
    """Manages loading and accessing source configurations."""

    def __init__(self, config_path: str = "config/sources.yaml"):
        self.config_path = config_path
        self.sources = []
        self._load_sources()

    def _load_sources(self):
        """Load sources from YAML configuration."""
        import yaml
        from pathlib import Path

        config_file = Path(__file__).parent.parent.parent / self.config_path

        with open(config_file, "r") as f:
            data = yaml.safe_load(f)
            self.sources = data.get("sources", [])

        logger.info(f"Loaded {len(self.sources)} sources from configuration")

    def get_active_sources(self) -> List[Dict[str, Any]]:
        """Get all active sources.

        Returns:
            List of source configurations
        """
        return [source for source in self.sources if source.get("active", True)]

    def get_source_by_id(self, source_id: str) -> Optional[Dict[str, Any]]:
        """Get source configuration by ID.

        Args:
            source_id: Source identifier

        Returns:
            Source configuration dictionary or None
        """
        for source in self.sources:
            if source["id"] == source_id:
                return source
        return None

    def get_sources_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """Get sources by priority level.

        Args:
            priority: Priority level (high, medium, low)

        Returns:
            List of source configurations
        """
        return [
            source
            for source in self.sources
            if source.get("priority") == priority and source.get("active", True)
        ]
