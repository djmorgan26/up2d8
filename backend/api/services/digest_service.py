"""
Digest Service

Handles digest generation and email rendering using Jinja2 templates.
"""

import os
from typing import Dict, Any
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import structlog

from api.services.email_provider import EmailMessage, get_email_client

logger = structlog.get_logger()


class DigestService:
    """
    Service for rendering and sending email digests.
    """

    def __init__(self):
        # Set up Jinja2 environment for email templates
        template_dir = Path(__file__).parent.parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )
        self.email_client = get_email_client()

    def render_digest_email(self, digest_data: Dict[str, Any]) -> str:
        """
        Render digest data into HTML email using Jinja2 template.

        Args:
            digest_data: Digest data from DigestBuilder

        Returns:
            Rendered HTML string
        """
        template = self.jinja_env.get_template("email_digest.html")
        html = template.render(**digest_data)
        return html

    async def send_digest(self, digest_data: Dict[str, Any]) -> bool:
        """
        Render and send a digest email.

        Args:
            digest_data: Digest data from DigestBuilder

        Returns:
            True if sent successfully
        """
        try:
            # Render HTML
            html_body = self.render_digest_email(digest_data)

            # Create email message
            subject = f"UP2D8 Daily Digest - {digest_data['digest_day']}"
            if digest_data.get('is_test'):
                subject = f"[TEST] {subject}"

            message = EmailMessage(
                to=digest_data['user_email'],
                subject=subject,
                html_body=html_body,
                from_email=os.getenv("FROM_EMAIL", "noreply@up2d8.ai"),
                text_body=self._generate_text_version(digest_data)
            )

            # Send email
            success = await self.email_client.send_email(message)

            if success:
                logger.info(
                    "digest_sent",
                    user_email=digest_data['user_email'],
                    article_count=digest_data['article_count']
                )
            else:
                logger.error(
                    "digest_send_failed",
                    user_email=digest_data['user_email']
                )

            return success

        except Exception as e:
            logger.error(
                "digest_send_exception",
                user_email=digest_data.get('user_email'),
                error=str(e),
                exc_info=True
            )
            return False

    def _generate_text_version(self, digest_data: Dict[str, Any]) -> str:
        """
        Generate plain text version of digest for email clients that don't support HTML.

        Args:
            digest_data: Digest data

        Returns:
            Plain text version
        """
        text_parts = [
            f"UP2D8 Daily Digest - {digest_data['digest_day']}",
            "=" * 60,
            "",
            f"Hello {digest_data['user_name']},",
            "",
            f"Here are your {digest_data['article_count']} curated articles for today:",
            "",
        ]

        for i, article in enumerate(digest_data['articles'], 1):
            text_parts.extend([
                f"{i}. {article['title']}",
                f"   Source: {article['source']}",
                f"   {article['summary'][:200]}...",
                f"   Read more: {article['url']}",
                "",
            ])

        text_parts.extend([
            "=" * 60,
            "UP2D8 - AI-Powered Industry Insights",
            "https://up2d8.ai",
        ])

        return "\n".join(text_parts)


def get_digest_service() -> DigestService:
    """Factory function to get DigestService instance."""
    return DigestService()
