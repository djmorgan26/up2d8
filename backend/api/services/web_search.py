"""
Web Search Service

Provides web search capabilities using Brave Search API (free tier).
Integrates with the conversational agent to provide real-time information.
"""
from typing import List, Dict, Any, Optional
import httpx
import os
import structlog
from datetime import datetime

logger = structlog.get_logger()


class WebSearchService:
    """
    Web search service using Brave Search API

    Free tier: 2,000 queries/month
    https://brave.com/search/api/
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize web search service

        Args:
            api_key: Brave Search API key (optional, reads from env)
        """
        self.api_key = api_key or os.getenv("BRAVE_API_KEY")
        self.base_url = "https://api.search.brave.com/res/v1/web/search"

        if not self.api_key:
            logger.warning("brave_api_key_not_set", message="Web search will not be available")

        logger.info("web_search_service_initialized", has_api_key=bool(self.api_key))

    async def search(
        self,
        query: str,
        count: int = 5,
        country: str = "us",
        freshness: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform web search

        Args:
            query: Search query
            count: Number of results (max 20 for free tier)
            country: Country code (us, uk, etc.)
            freshness: Time filter (pd=past day, pw=past week, pm=past month, py=past year)

        Returns:
            Search results with web pages and metadata
        """
        if not self.api_key:
            logger.warning("search_skipped_no_api_key", query=query)
            return {
                "results": [],
                "error": "Brave API key not configured"
            }

        try:
            params = {
                "q": query,
                "count": min(count, 20),  # Free tier max
                "country": country,
            }

            if freshness:
                params["freshness"] = freshness

            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.api_key
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    self.base_url,
                    params=params,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()

            # Extract web results
            web_results = data.get("web", {}).get("results", [])

            results = []
            for item in web_results:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "description": item.get("description", ""),
                    "age": item.get("age", ""),
                    "language": item.get("language", ""),
                })

            logger.info(
                "web_search_completed",
                query=query,
                results_count=len(results)
            )

            return {
                "query": query,
                "results": results,
                "timestamp": datetime.utcnow().isoformat(),
                "count": len(results)
            }

        except httpx.HTTPStatusError as e:
            logger.error(
                "web_search_http_error",
                query=query,
                status_code=e.response.status_code,
                error=str(e)
            )
            return {
                "results": [],
                "error": f"HTTP error: {e.response.status_code}"
            }
        except Exception as e:
            logger.error("web_search_error", query=query, error=str(e))
            return {
                "results": [],
                "error": str(e)
            }

    async def search_for_context(
        self,
        query: str,
        num_results: int = 3
    ) -> str:
        """
        Search web and format results as context for LLM

        Args:
            query: Search query
            num_results: Number of results to include

        Returns:
            Formatted context string
        """
        search_results = await self.search(query, count=num_results)

        if search_results.get("error") or not search_results.get("results"):
            return "No web search results available."

        results = search_results["results"]

        context_parts = [
            f"Web search results for '{query}':\n"
        ]

        for i, result in enumerate(results, 1):
            context_parts.append(
                f"{i}. {result['title']}\n"
                f"   {result['description']}\n"
                f"   Source: {result['url']}\n"
            )

        return "\n".join(context_parts)

    def is_available(self) -> bool:
        """Check if web search is available"""
        return bool(self.api_key)


# Singleton instance
_web_search_service: Optional[WebSearchService] = None


def get_web_search_service() -> WebSearchService:
    """
    Get or create web search service instance

    Returns:
        WebSearchService instance
    """
    global _web_search_service

    if _web_search_service is None:
        _web_search_service = WebSearchService()

    return _web_search_service
