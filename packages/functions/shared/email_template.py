"""
Email templates for Up2D8 newsletter
"""

def get_newsletter_template(articles: list, user_name: str = "there") -> str:
    """
    Generate a beautiful HTML email template for the newsletter.

    Args:
        articles: List of article dicts with 'title', 'summary', 'link', 'published'
        user_name: Name to greet the user with

    Returns:
        HTML string for the email
    """

    # Build article HTML
    articles_html = ""
    for idx, article in enumerate(articles, 1):
        title = article.get('title', 'Untitled')
        summary = article.get('summary', '')
        link = article.get('link') or article.get('url', '#')
        published = article.get('published', '')

        articles_html += f"""
        <tr>
            <td style="padding: 20px 0; border-bottom: 1px solid #e5e7eb;">
                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                        <td style="padding-bottom: 8px;">
                            <span style="display: inline-block; background-color: #3b82f6; color: white; font-size: 12px; font-weight: 600; padding: 4px 12px; border-radius: 12px; margin-right: 8px;">#{idx}</span>
                            <a href="{link}" style="color: #1f2937; font-size: 18px; font-weight: 600; text-decoration: none; line-height: 1.4;">
                                {title}
                            </a>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding-top: 8px; padding-bottom: 12px;">
                            <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.6;">
                                {summary}
                            </p>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <a href="{link}" style="display: inline-block; background-color: #3b82f6; color: white; text-decoration: none; padding: 10px 24px; border-radius: 6px; font-size: 14px; font-weight: 500; transition: background-color 0.2s;">
                                Read Article →
                            </a>
                            {f'<span style="color: #9ca3af; font-size: 12px; margin-left: 12px;">{published}</span>' if published else ''}
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        """

    # Main template
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Your Daily News Digest</title>
        <!--[if mso]>
        <style type="text/css">
            body, table, td {{font-family: Arial, sans-serif !important;}}
        </style>
        <![endif]-->
    </head>
    <body style="margin: 0; padding: 0; background-color: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f3f4f6; padding: 20px 0;">
            <tr>
                <td align="center">
                    <!-- Main container -->
                    <table width="600" cellpadding="0" cellspacing="0" border="0" style="background-color: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden; max-width: 100%;">

                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); padding: 40px 30px; text-align: center;">
                                <h1 style="margin: 0; color: white; font-size: 32px; font-weight: 700; letter-spacing: -0.5px;">
                                    📰 Up2D8
                                </h1>
                                <p style="margin: 8px 0 0 0; color: #dbeafe; font-size: 16px;">
                                    Your Personalized News Digest
                                </p>
                            </td>
                        </tr>

                        <!-- Greeting -->
                        <tr>
                            <td style="padding: 30px 30px 20px 30px;">
                                <h2 style="margin: 0; color: #1f2937; font-size: 24px; font-weight: 600;">
                                    Hello {user_name}! 👋
                                </h2>
                                <p style="margin: 12px 0 0 0; color: #6b7280; font-size: 16px; line-height: 1.6;">
                                    Here are your top stories for today, curated based on your interests.
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
                            <td style="padding: 30px; background-color: #1f2937; text-align: center;">
                                <p style="margin: 0 0 12px 0; color: #9ca3af; font-size: 14px;">
                                    You're receiving this email because you subscribed to Up2D8 newsletters.
                                </p>
                                <p style="margin: 0; color: #6b7280; font-size: 12px;">
                                    <a href="https://gray-wave-00bdfc60f.3.azurestaticapps.net/settings" style="color: #60a5fa; text-decoration: none;">Manage your preferences</a> •
                                    <a href="https://gray-wave-00bdfc60f.3.azurestaticapps.net" style="color: #60a5fa; text-decoration: none;">Visit Up2D8</a>
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
