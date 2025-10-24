"""
AI-powered article summarization service.

Generates multi-level summaries with timeout handling for slow models:
- Micro (280 chars) - Tweet-length
- Standard (150-200 words) - Email digest
- Detailed (300-500 words) - Full context

Optimized for free-tier models (Ollama) with aggressive timeout and retry logic.
"""

import asyncio
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import structlog

from api.services.llm_provider import get_llm_client

logger = structlog.get_logger()


class SummarizationError(Exception):
    """Base exception for summarization errors."""
    pass


class TimeoutError(SummarizationError):
    """Raised when summarization times out."""
    pass


class Summarizer:
    """
    Article summarization service with timeout handling.

    Uses a tiered approach for slow models:
    1. Try all 3 summaries together (fastest)
    2. If timeout, try summaries individually with shorter timeouts
    3. If still failing, generate minimal summaries
    """

    def __init__(
        self,
        max_timeout: int = 120,  # 2 minutes max for all summaries
        micro_timeout: int = 30,  # 30 seconds for micro
        standard_timeout: int = 45,  # 45 seconds for standard
        detailed_timeout: int = 60,  # 60 seconds for detailed
    ):
        self.llm_client = get_llm_client()
        self.max_timeout = max_timeout
        self.micro_timeout = micro_timeout
        self.standard_timeout = standard_timeout
        self.detailed_timeout = detailed_timeout

    async def summarize_article(
        self,
        title: str,
        content: str,
        author: Optional[str] = None,
        published_at: Optional[datetime] = None,
    ) -> Dict[str, str]:
        """
        Generate all three summary levels for an article.

        Returns:
            {
                "summary_micro": str (280 chars),
                "summary_standard": str (150-200 words),
                "summary_detailed": str (300-500 words)
            }
        """
        logger.info(
            "Starting article summarization",
            title=title[:100],
            content_length=len(content),
        )

        # Strategy 1: Try generating all summaries at once (most efficient)
        try:
            summaries = await asyncio.wait_for(
                self._generate_all_summaries(title, content, author),
                timeout=self.max_timeout,
            )
            logger.info("Successfully generated all summaries in one pass")
            return summaries
        except asyncio.TimeoutError:
            logger.warning(
                "Timeout generating all summaries at once, falling back to individual generation"
            )
        except Exception as e:
            logger.warning(f"Error generating all summaries at once: {e}")

        # Strategy 2: Generate summaries individually with shorter timeouts
        summaries = {}

        # Micro summary (highest priority - always try)
        try:
            summaries["summary_micro"] = await asyncio.wait_for(
                self._generate_micro_summary(title, content),
                timeout=self.micro_timeout,
            )
        except asyncio.TimeoutError:
            logger.error("Timeout generating micro summary, using fallback")
            summaries["summary_micro"] = self._fallback_micro_summary(title, content)
        except Exception as e:
            logger.error(f"Error generating micro summary: {e}")
            summaries["summary_micro"] = self._fallback_micro_summary(title, content)

        # Standard summary (medium priority)
        try:
            summaries["summary_standard"] = await asyncio.wait_for(
                self._generate_standard_summary(title, content),
                timeout=self.standard_timeout,
            )
        except asyncio.TimeoutError:
            logger.error("Timeout generating standard summary, using fallback")
            summaries["summary_standard"] = self._fallback_standard_summary(title, content)
        except Exception as e:
            logger.error(f"Error generating standard summary: {e}")
            summaries["summary_standard"] = self._fallback_standard_summary(title, content)

        # Detailed summary (lowest priority - skip if time-constrained)
        try:
            summaries["summary_detailed"] = await asyncio.wait_for(
                self._generate_detailed_summary(title, content),
                timeout=self.detailed_timeout,
            )
        except asyncio.TimeoutError:
            logger.error("Timeout generating detailed summary, using fallback")
            summaries["summary_detailed"] = self._fallback_detailed_summary(title, content)
        except Exception as e:
            logger.error(f"Error generating detailed summary: {e}")
            summaries["summary_detailed"] = self._fallback_detailed_summary(title, content)

        logger.info(
            "Completed article summarization",
            micro_length=len(summaries.get("summary_micro", "")),
            standard_length=len(summaries.get("summary_standard", "")),
            detailed_length=len(summaries.get("summary_detailed", "")),
        )

        return summaries

    async def _generate_all_summaries(
        self, title: str, content: str, author: Optional[str]
    ) -> Dict[str, str]:
        """Generate all three summary levels in one LLM call (most efficient)."""

        # Truncate content if too long (Ollama free models have context limits)
        max_content_length = 4000  # characters
        truncated_content = content[:max_content_length]
        if len(content) > max_content_length:
            truncated_content += "... [content truncated]"

        author_info = f"Author: {author}\n" if author else ""

        prompt = f"""Summarize this article at three different levels of detail.

{author_info}Title: {title}

Content:
{truncated_content}

Generate THREE summaries:

1. MICRO (exactly 280 characters or less - for social media):
[Write a concise, punchy summary that captures the core insight]

2. STANDARD (150-200 words - for email digest):
[Write a clear, informative summary covering main points]

3. DETAILED (300-500 words - for full context):
[Write a comprehensive summary with key details, implications, and context]

Format your response EXACTLY like this:
MICRO: [your 280-char summary]
STANDARD: [your 150-200 word summary]
DETAILED: [your 300-500 word summary]"""

        response = await self.llm_client.generate(
            prompt=prompt,
            max_tokens=800,  # Enough for all three summaries
            temperature=0.3,  # Lower for more consistent output
        )

        # Parse response
        summaries = self._parse_multi_summary_response(response)

        # Validate we got all three
        if not all(k in summaries for k in ["summary_micro", "summary_standard", "summary_detailed"]):
            raise ValueError("Failed to parse all three summary levels")

        return summaries

    async def _generate_micro_summary(self, title: str, content: str) -> str:
        """Generate micro (280 char) summary."""
        truncated_content = content[:2000]

        prompt = f"""Summarize this article in EXACTLY 280 characters or less (like a tweet).

Title: {title}
Content: {truncated_content}

Write a punchy, engaging summary that captures the key insight:"""

        response = await self.llm_client.generate(
            prompt=prompt,
            max_tokens=100,
            temperature=0.5,
        )

        # Ensure it's actually 280 chars or less
        summary = response.strip()
        if len(summary) > 280:
            summary = summary[:277] + "..."

        return summary

    async def _generate_standard_summary(self, title: str, content: str) -> str:
        """Generate standard (150-200 word) summary."""
        truncated_content = content[:3000]

        prompt = f"""Summarize this article in 150-200 words for an email digest.

Title: {title}
Content: {truncated_content}

Write a clear, informative summary covering the main points:"""

        response = await self.llm_client.generate(
            prompt=prompt,
            max_tokens=300,
            temperature=0.4,
        )

        return response.strip()

    async def _generate_detailed_summary(self, title: str, content: str) -> str:
        """Generate detailed (300-500 word) summary."""
        truncated_content = content[:4000]

        prompt = f"""Summarize this article in 300-500 words with full context.

Title: {title}
Content: {truncated_content}

Write a comprehensive summary including key details, implications, and context:"""

        response = await self.llm_client.generate(
            prompt=prompt,
            max_tokens=600,
            temperature=0.3,
        )

        return response.strip()

    def _parse_multi_summary_response(self, response: str) -> Dict[str, str]:
        """Parse LLM response with multiple summaries."""
        summaries = {}

        # Try to extract each section
        lines = response.split("\n")
        current_type = None
        current_text = []

        for line in lines:
            line = line.strip()

            if line.startswith("MICRO:"):
                if current_type and current_text:
                    summaries[f"summary_{current_type.lower()}"] = " ".join(current_text).strip()
                current_type = "MICRO"
                current_text = [line.replace("MICRO:", "").strip()]
            elif line.startswith("STANDARD:"):
                if current_type and current_text:
                    summaries[f"summary_{current_type.lower()}"] = " ".join(current_text).strip()
                current_type = "STANDARD"
                current_text = [line.replace("STANDARD:", "").strip()]
            elif line.startswith("DETAILED:"):
                if current_type and current_text:
                    summaries[f"summary_{current_type.lower()}"] = " ".join(current_text).strip()
                current_type = "DETAILED"
                current_text = [line.replace("DETAILED:", "").strip()]
            elif current_type and line:
                current_text.append(line)

        # Add last section
        if current_type and current_text:
            summaries[f"summary_{current_type.lower()}"] = " ".join(current_text).strip()

        # Validate micro length
        if "summary_micro" in summaries and len(summaries["summary_micro"]) > 280:
            summaries["summary_micro"] = summaries["summary_micro"][:277] + "..."

        return summaries

    def _fallback_micro_summary(self, title: str, content: str) -> str:
        """Fallback micro summary using simple truncation."""
        # Try to create a basic summary from title + first sentence
        first_sentence = content.split(".")[0] if content else ""
        summary = f"{title}. {first_sentence}".strip()

        if len(summary) > 280:
            summary = summary[:277] + "..."

        logger.info("Using fallback micro summary", length=len(summary))
        return summary

    def _fallback_standard_summary(self, title: str, content: str) -> str:
        """Fallback standard summary using first few sentences."""
        sentences = content.split(".")[:5] if content else []
        summary = ". ".join(sentences).strip()

        # Aim for ~150 words
        words = summary.split()[:150]
        summary = " ".join(words)

        if not summary.endswith("."):
            summary += "..."

        logger.info("Using fallback standard summary", word_count=len(summary.split()))
        return summary

    def _fallback_detailed_summary(self, title: str, content: str) -> str:
        """Fallback detailed summary using first several sentences."""
        sentences = content.split(".")[:10] if content else []
        summary = ". ".join(sentences).strip()

        # Aim for ~300 words
        words = summary.split()[:300]
        summary = " ".join(words)

        if not summary.endswith("."):
            summary += "..."

        logger.info("Using fallback detailed summary", word_count=len(summary.split()))
        return summary


# Factory function
def get_summarizer(**kwargs) -> Summarizer:
    """Get a configured Summarizer instance."""
    return Summarizer(**kwargs)
