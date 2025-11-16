"""
Email templates for Up2D8 newsletter
"""

def get_newsletter_template(
    articles: list,
    user_name: str = "there",
    newsletter_format: str = "concise",
    user_topics: list = None,
    unsubscribe_url: str = "https://gray-wave-00bdfc60f.3.azurestaticapps.net/settings",
    feedback_url: str = "https://gray-wave-00bdfc60f.3.azurestaticapps.net/api/feedback",
    variant: str = "A"
) -> str:
    """
    Generate a beautiful, mobile-responsive HTML email template for the newsletter.

    Args:
        articles: List of article dicts with fields:
            - title: Article title
            - summary: Article summary
            - link/url: Article URL
            - published: Published date string
            - image_url: Preview image URL (optional)
            - topic: Matched topic category (optional)
            - source: Article source name (optional)
            - read_time: Estimated read time (optional)
            - published_time_ago: Relative time string (optional)
            - id: Article ID for feedback (optional)
        user_name: Name to greet the user with
        newsletter_format: 'concise' or 'detailed' - affects summary length and metadata
        user_topics: List of user's topic preferences for personalization
        unsubscribe_url: URL for unsubscribe action (legal requirement)
        feedback_url: URL for article feedback
        variant: A/B testing variant ('A', 'B', or 'C')

    Returns:
        HTML string for the email with mobile-responsive design
    """

    # Initialize defaults
    if user_topics is None:
        user_topics = []

    # Configure format-specific settings
    if newsletter_format == "concise":
        max_summary_chars = 150
        show_metadata = False
        show_feedback = False
    else:  # detailed
        max_summary_chars = 400
        show_metadata = True
        show_feedback = True

    # Variant-specific header configuration
    variant_config = {
        'A': {'emoji': '📰', 'tagline': 'Your Personalized News Digest'},
        'B': {'emoji': '🗞️', 'tagline': 'Today\'s Top Stories'},
        'C': {'emoji': '✨', 'tagline': f'{user_name}\'s Daily Briefing'}
    }
    header_config = variant_config.get(variant, variant_config['A'])

    # Build article HTML
    articles_html = ""
    for idx, article in enumerate(articles, 1):
        title = article.get('title', 'Untitled')
        summary = article.get('summary', '')
        link = article.get('link') or article.get('url', '#')
        published = article.get('published', '')
        image_url = article.get('image_url', '')
        topic = article.get('topic', '')
        source = article.get('source', '')
        read_time = article.get('read_time', '')
        published_time_ago = article.get('published_time_ago', '')
        article_id = article.get('id', idx)

        # Truncate summary if needed
        if len(summary) > max_summary_chars:
            summary = summary[:max_summary_chars].rsplit(' ', 1)[0] + "..."

        # Build topic badge
        topic_badge = ""
        if topic:
            topic_badge = f'''<span style="display: inline-block; background-color: #e0f2fe; color: #0369a1; font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 10px; margin-right: 8px;">{topic}</span>'''

        # Build metadata line
        metadata_html = ""
        if show_metadata and (source or published_time_ago or read_time):
            metadata_parts = []
            if source:
                metadata_parts.append(source)
            if published_time_ago:
                metadata_parts.append(published_time_ago)
            if read_time:
                metadata_parts.append(f"📖 {read_time}")
            metadata_html = f'''
                    <tr>
                        <td style="padding-top: 4px; padding-bottom: 8px;">
                            <span style="color: #9ca3af; font-size: 12px;">
                                {' • '.join(metadata_parts)}
                            </span>
                        </td>
                    </tr>'''

        # Build feedback buttons
        feedback_html = ""
        if show_feedback:
            feedback_html = f'''
                    <tr>
                        <td style="padding-top: 12px;">
                            <p style="font-size: 12px; color: #9ca3af; margin: 0 0 8px 0;">
                                Was this article helpful?
                            </p>
                            <a href="{feedback_url}?article={article_id}&rating=up"
                               style="display: inline-block; padding: 6px 12px; background: #f0fdf4; color: #16a34a; text-decoration: none; border-radius: 4px; font-size: 11px; margin-right: 8px;">
                                👍 Helpful
                            </a>
                            <a href="{feedback_url}?article={article_id}&rating=down"
                               style="display: inline-block; padding: 6px 12px; background: #fef2f2; color: #dc2626; text-decoration: none; border-radius: 4px; font-size: 11px;">
                                👎 Not relevant
                            </a>
                        </td>
                    </tr>'''

        # Build preview image
        image_html = ""
        if image_url:
            image_html = f'''
                    <tr>
                        <td style="padding-bottom: 12px;">
                            <a href="{link}" style="display: block;">
                                <img src="{image_url}"
                                     alt="{title} - Article preview image"
                                     width="100%"
                                     style="max-width: 100%; height: auto; border-radius: 8px; display: block;" />
                            </a>
                        </td>
                    </tr>'''

        articles_html += f"""
        <tr>
            <td style="padding: 20px 0; border-bottom: 1px solid #e5e7eb;" class="article-container">
                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                    {image_html}
                    <tr>
                        <td style="padding-bottom: 8px;">
                            {topic_badge}<span style="display: inline-block; background-color: #3b82f6; color: white; font-size: 12px; font-weight: 600; padding: 4px 12px; border-radius: 12px; margin-right: 8px;">#{idx}</span>
                            <a href="{link}"
                               aria-label="Read full article: {title}"
                               class="article-title"
                               style="color: #1f2937; font-size: 18px; font-weight: 600; text-decoration: none; line-height: 1.4;">
                                {title}
                            </a>
                        </td>
                    </tr>
                    {metadata_html}
                    <tr>
                        <td style="padding-top: 8px; padding-bottom: 12px;">
                            <p class="article-summary" style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.6; max-width: 540px;">
                                {summary}
                            </p>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <a href="{link}"
                               aria-label="Read full article: {title}"
                               class="button"
                               style="display: inline-block; background-color: #3b82f6; color: white; text-decoration: none; padding: 10px 24px; border-radius: 6px; font-size: 14px; font-weight: 500;">
                                Read Article →
                            </a>
                        </td>
                    </tr>
                    {feedback_html}
                </table>
            </td>
        </tr>
        """

    # Build personalization message
    article_count = len(articles)
    topic_display = ', '.join(user_topics[:3]) if user_topics else 'your interests'
    personalization_msg = f"We found {article_count} articles about <strong>{topic_display}</strong> that we think you'll love."

    # Build preheader text (hidden but shown in email preview)
    preheader_text = f"{article_count} personalized stories"
    if user_topics:
        preheader_text += f" about {', '.join(user_topics[:2])}"
    preheader_text += " and more. Your daily digest is ready!"

    # Main template
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="color-scheme" content="light dark">
        <meta name="supported-color-schemes" content="light dark">
        <title>Your Daily News Digest</title>
        <!--[if mso]>
        <style type="text/css">
            body, table, td {{font-family: Arial, sans-serif !important;}}
        </style>
        <![endif]-->
        <style type="text/css">
            /* Mobile-first responsive styles */
            @media only screen and (max-width: 600px) {{
                .container {{
                    width: 100% !important;
                    max-width: 100% !important;
                }}
                .article-title {{
                    font-size: 16px !important;
                }}
                .article-summary {{
                    font-size: 13px !important;
                }}
                .button {{
                    padding: 12px 20px !important;
                    font-size: 13px !important;
                }}
                .header-title {{
                    font-size: 24px !important;
                }}
                .padding-mobile {{
                    padding: 20px 15px !important;
                }}
                .article-container {{
                    padding: 15px 0 !important;
                }}
            }}

            /* Dark mode support */
            @media (prefers-color-scheme: dark) {{
                .dark-mode-bg {{
                    background-color: #1f2937 !important;
                }}
                .dark-mode-text {{
                    color: #e5e7eb !important;
                }}
                .dark-mode-card {{
                    background-color: #374151 !important;
                }}
                .dark-mode-border {{
                    border-color: #4b5563 !important;
                }}
            }}
        </style>
    </head>
    <body style="margin: 0; padding: 0; background-color: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;" class="dark-mode-bg">
        <!-- Preheader text (hidden but shown in preview) -->
        <div style="display: none; max-height: 0px; overflow: hidden; mso-hide: all;" aria-hidden="true">
            {preheader_text}
        </div>

        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f3f4f6; padding: 20px 0;" class="dark-mode-bg">
            <tr>
                <td align="center">
                    <!-- Main container -->
                    <table width="600" cellpadding="0" cellspacing="0" border="0" class="container dark-mode-card" style="background-color: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden; max-width: 100%;">

                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); padding: 40px 30px; text-align: center;" class="padding-mobile">
                                <h1 class="header-title" style="margin: 0; color: white; font-size: 32px; font-weight: 700; letter-spacing: -0.5px;" aria-label="Up2D8 Newsletter">
                                    {header_config['emoji']} Up2D8
                                </h1>
                                <p style="margin: 8px 0 0 0; color: #dbeafe; font-size: 16px;">
                                    {header_config['tagline']}
                                </p>
                            </td>
                        </tr>

                        <!-- Greeting -->
                        <tr>
                            <td style="padding: 30px 30px 20px 30px;" class="padding-mobile dark-mode-card">
                                <h2 class="dark-mode-text" style="margin: 0; color: #1f2937; font-size: 24px; font-weight: 600;">
                                    Hello {user_name}! 👋
                                </h2>
                                <p class="dark-mode-text" style="margin: 12px 0 0 0; color: #6b7280; font-size: 16px; line-height: 1.6; max-width: 540px;">
                                    {personalization_msg}
                                </p>
                            </td>
                        </tr>

                        <!-- Articles -->
                        <tr>
                            <td style="padding: 0 30px;">
                                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                    {articles_html}
                                </table>
                            </td>
                        </tr>

                        <!-- Chat Button -->
                        <tr>
                            <td style="padding: 40px 30px; background-color: #f9fafb; text-align: center;">
                                <p style="margin: 0 0 20px 0; color: #4b5563; font-size: 16px; font-weight: 500;">
                                    Want to dive deeper? Chat with our AI assistant!
                                </p>
                                <a href="https://gray-wave-00bdfc60f.3.azurestaticapps.net"
                                   style="display: inline-block; background-color: #10b981; color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-size: 16px; font-weight: 600; box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);">
                                    💬 Chat with AI Assistant
                                </a>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="padding: 30px; background-color: #1f2937; text-align: center;" class="padding-mobile">
                                <p style="margin: 0 0 12px 0; color: #9ca3af; font-size: 14px;">
                                    You're receiving this email because you subscribed to Up2D8 newsletters.
                                </p>
                                <p style="margin: 0; color: #6b7280; font-size: 12px;">
                                    <a href="https://gray-wave-00bdfc60f.3.azurestaticapps.net/settings"
                                       style="color: #60a5fa; text-decoration: none;"
                                       aria-label="Manage your email preferences">Manage your preferences</a> •
                                    <a href="https://gray-wave-00bdfc60f.3.azurestaticapps.net"
                                       style="color: #60a5fa; text-decoration: none;"
                                       aria-label="Visit Up2D8 website">Visit Up2D8</a> •
                                    <a href="{unsubscribe_url}"
                                       style="color: #60a5fa; text-decoration: none;"
                                       aria-label="Unsubscribe from newsletter">Unsubscribe</a>
                                </p>
                                <p style="margin: 16px 0 0 0; color: #6b7280; font-size: 12px;">
                                    © 2025 Up2D8. All rights reserved.
                                </p>
                            </td>
                        </tr>

                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    return html_template


def get_plain_text_newsletter(articles: list, user_name: str = "there") -> str:
    """
    Generate a plain text version of the newsletter for email clients that don't support HTML.

    Args:
        articles: List of article dicts with 'title', 'summary', 'link'
        user_name: Name to greet the user with

    Returns:
        Plain text string for the email
    """

    text = f"""
UP2D8 - Your Personalized News Digest
{'=' * 50}

Hello {user_name}!

Here are your top stories for today, curated based on your interests:

"""

    for idx, article in enumerate(articles, 1):
        title = article.get('title', 'Untitled')
        summary = article.get('summary', '')
        link = article.get('link') or article.get('url', '')

        text += f"""
[{idx}] {title}
{'-' * 50}
{summary}

Read more: {link}

"""

    text += f"""
{'=' * 50}

Want to dive deeper? Chat with our AI assistant!
Visit: https://gray-wave-00bdfc60f.3.azurestaticapps.net

---
You're receiving this email because you subscribed to Up2D8 newsletters.
Manage your preferences: https://gray-wave-00bdfc60f.3.azurestaticapps.net/settings

© 2025 Up2D8. All rights reserved.
"""

    return text
