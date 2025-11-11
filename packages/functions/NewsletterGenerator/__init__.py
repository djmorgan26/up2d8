import os
import pymongo
import google.generativeai as genai
import azure.functions as func
import markdown # Import the markdown library
from shared.email_service import EmailMessage, SMTPProvider
from dotenv import load_dotenv
from shared.key_vault_client import get_secret_client
import structlog
from shared.logger_config import configure_logger
from datetime import datetime

# Configure structlog
configure_logger()
logger = structlog.get_logger()

def should_send_newsletter(frequency: str, last_sent: datetime = None) -> bool:
    """Determine if newsletter should be sent based on frequency."""
    now = datetime.utcnow()

    if frequency == "daily":
        return True  # Always send on daily schedule
    elif frequency == "weekly":
        # Send only on Mondays (0 = Monday)
        return now.weekday() == 0
    elif frequency == "monthly":
        # Send only on 1st of month
        return now.day == 1
    else:
        return True  # Default to daily

def main(timer: func.TimerRequest) -> None:
    load_dotenv()
    logger.info('Python timer trigger function ran', past_due=timer.past_due)
    logger.info('NewsletterGenerator function is executing.')

    try:
        # Get configuration from environment variables and Key Vault
        secret_client = get_secret_client()

        cosmos_db_connection_string = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value
        gemini_api_key = secret_client.get_secret("UP2D8-GEMINI-API-Key").value
        brevo_smtp_user = os.environ["BREVO_SMTP_USER"]
        brevo_smtp_password = secret_client.get_secret("UP2D8-SMTP-KEY").value
        brevo_smtp_host = os.environ["BREVO_SMTP_HOST"]
        brevo_smtp_port = int(os.environ["BREVO_SMTP_PORT"])
        sender_email = os.environ["SENDER_EMAIL"]

        # Configure Gemini API
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Initialize SMTP Provider
        smtp_provider = SMTPProvider(
            smtp_host=brevo_smtp_host,
            smtp_port=brevo_smtp_port,
            smtp_username=brevo_smtp_user,
            smtp_password=brevo_smtp_password
        )

        # Connect to Cosmos DB
        client = pymongo.MongoClient(cosmos_db_connection_string)
        db = client.up2d8
        users_collection = db.users
        articles_collection = db.articles

        # Fetch users and unprocessed articles
        users = list(users_collection.find())
        articles = list(articles_collection.find({'processed': False}))

        if not articles:
            logger.info("No new articles to process.")
            return

        sent_newsletters_count = 0
        for user in users:
            try:
                # Get user topics and preferences (new schema)
                user_topics = user.get('topics', [])
                user_preferences = user.get('preferences', {})

                # Get newsletter settings
                newsletter_format = user_preferences.get('newsletter_format', 'concise')
                newsletter_frequency = user_preferences.get('newsletter_frequency', 'daily')
                email_notifications = user_preferences.get('email_notifications', True)

                # Check if user has email notifications enabled
                if not email_notifications:
                    logger.info("Email notifications disabled for user", user_email=user['email'])
                    continue

                # Check if newsletter should be sent based on frequency
                if not should_send_newsletter(newsletter_frequency):
                    logger.info("Skipping user due to frequency setting",
                               user_email=user['email'],
                               frequency=newsletter_frequency)
                    continue

                # Filter articles based on topics
                relevant_articles = [a for a in articles if any(topic.lower() in a.get('title', '').lower() or
                                                                 topic.lower() in a.get('summary', '').lower()
                                                                 for topic in user_topics)]

                if not relevant_articles:
                    logger.info("No relevant articles for user", user_email=user['email'], topics=user_topics)
                    continue

                # Generate newsletter content with Gemini
                prompt = f"Create a {newsletter_format} newsletter in Markdown from these articles:\n\n"
                for article in relevant_articles:
                    prompt += f"- **{article['title']}**: {article['summary']}\n"
                
                newsletter_content_markdown = ""
                try:
                    response = model.generate_content(prompt)
                    newsletter_content_markdown = response.text
                except Exception as e:
                    logger.error("Error generating content with Gemini for user", user_email=user['email'], error=str(e))
                    continue # Skip to the next user if Gemini API fails

                if not newsletter_content_markdown:
                    logger.warning("Gemini API returned empty content for user. Skipping email.", user_email=user['email'])
                    continue

                # Convert Markdown to HTML
                newsletter_content_html = markdown.markdown(newsletter_content_markdown)

                # Create and send email
                email_message = EmailMessage(
                    to=user['email'],
                    subject='Your Daily News Digest',
                    html_body=newsletter_content_html, # Use HTML content
                    from_email=sender_email
                )
                
                # Note: The send_email method in SMTPProvider is not async, so we call it directly.
                if smtp_provider.send_email(email_message):
                    sent_newsletters_count += 1
                    logger.info("Newsletter sent", user_email=user['email'])
                else:
                    logger.error("Failed to send newsletter", user_email=user['email'])

            except Exception as e:
                logger.error("Error processing user", user_email=user['email'], error=str(e))

        # Mark articles as processed
        article_ids = [a['_id'] for a in articles]
        articles_collection.update_many({'_id': {'$in': article_ids}}, {'$set': {'processed': True}})

        logger.info('Sent newsletters', count=sent_newsletters_count)

    except Exception as e:
        logger.error('An error occurred in NewsletterGenerator', error=str(e))

    logger.info('NewsletterGenerator function execution finished.')
