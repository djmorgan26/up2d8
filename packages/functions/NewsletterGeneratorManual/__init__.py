import os
import pymongo
import google.generativeai as genai
import azure.functions as func
import markdown
from shared.email_service import EmailMessage, SMTPProvider
from dotenv import load_dotenv
from shared.key_vault_client import get_secret_client
import structlog
from shared.logger_config import configure_logger
from datetime import datetime
import json

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

def main(req: func.HttpRequest) -> func.HttpResponse:
    """HTTP-triggered version of newsletter generator for manual testing."""
    load_dotenv()
    logger.info('Manual NewsletterGenerator triggered via HTTP')

    try:
        # Get optional parameters from request
        force_send = req.params.get('force', 'false').lower() == 'true'
        test_email = req.params.get('email')

        logger.info('Request parameters', force_send=force_send, test_email=test_email)

        # Get configuration from environment variables and Key Vault
        secret_client = get_secret_client()

        cosmos_db_connection_string = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value
        gemini_api_key = secret_client.get_secret("UP2D8-GEMINI-API-Key").value
        brevo_smtp_user = os.environ["BREVO_SMTP_USER"]
        brevo_smtp_password = secret_client.get_secret("UP2D8-SMTP-KEY").value
        brevo_smtp_host = os.environ["BREVO_SMTP_HOST"]
        brevo_smtp_port = int(os.environ["BREVO_SMTP_PORT"])
        sender_email = os.environ["SENDER_EMAIL"]

        logger.info('Configuration loaded successfully')

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

        logger.info('Connected to Cosmos DB')

        # Fetch users and unprocessed articles
        users = list(users_collection.find())
        articles = list(articles_collection.find({'processed': False}))

        logger.info('Data fetched',
                   total_users=len(users),
                   unprocessed_articles=len(articles))

        if not articles:
            message = "No new articles to process."
            logger.warning(message)
            return func.HttpResponse(
                json.dumps({
                    "status": "warning",
                    "message": message,
                    "users": len(users),
                    "articles": 0,
                    "sent": 0
                }),
                mimetype="application/json",
                status_code=200
            )

        sent_newsletters_count = 0
        skipped_users = []
        errors = []

        for user in users:
            try:
                user_email = user.get('email', 'UNKNOWN')

                # If test_email is specified, only process that user
                if test_email and user_email != test_email:
                    continue

                logger.info("Processing user", user_email=user_email)

                # Get user topics and preferences
                user_topics = user.get('topics', [])
                user_preferences = user.get('preferences', {})

                # Get newsletter settings
                newsletter_format = user_preferences.get('newsletter_format', 'concise')
                newsletter_frequency = user_preferences.get('newsletter_frequency', 'daily')
                email_notifications = user_preferences.get('email_notifications', True)

                logger.info("User settings",
                           user_email=user_email,
                           topics=user_topics,
                           email_notifications=email_notifications,
                           frequency=newsletter_frequency,
                           format=newsletter_format)

                # Check if user has email notifications enabled (skip if force=false)
                if not email_notifications and not force_send:
                    reason = "Email notifications disabled"
                    logger.info(reason, user_email=user_email)
                    skipped_users.append({"email": user_email, "reason": reason})
                    continue

                # Check if newsletter should be sent based on frequency (skip if force=false)
                if not should_send_newsletter(newsletter_frequency) and not force_send:
                    reason = f"Frequency setting: {newsletter_frequency}"
                    logger.info("Skipping user due to frequency setting",
                               user_email=user_email,
                               frequency=newsletter_frequency)
                    skipped_users.append({"email": user_email, "reason": reason})
                    continue

                # Filter articles based on topics
                relevant_articles = [a for a in articles if any(topic.lower() in a.get('title', '').lower() or
                                                                 topic.lower() in a.get('summary', '').lower()
                                                                 for topic in user_topics)]

                logger.info("Articles filtered",
                           user_email=user_email,
                           relevant_count=len(relevant_articles))

                if not relevant_articles:
                    reason = f"No articles matching topics: {user_topics}"
                    logger.info("No relevant articles for user",
                               user_email=user_email,
                               topics=user_topics)
                    skipped_users.append({"email": user_email, "reason": reason})
                    continue

                # Generate newsletter content with Gemini
                prompt = f"Create a {newsletter_format} newsletter in Markdown from these articles:\n\n"
                for article in relevant_articles:
                    prompt += f"- **{article['title']}**: {article['summary']}\n"

                logger.info("Generating newsletter with Gemini", user_email=user_email)

                newsletter_content_markdown = ""
                try:
                    response = model.generate_content(prompt)
                    newsletter_content_markdown = response.text
                    logger.info("Newsletter generated successfully", user_email=user_email)
                except Exception as e:
                    error_msg = f"Gemini API error: {str(e)}"
                    logger.error(error_msg, user_email=user_email, error=str(e))
                    errors.append({"email": user_email, "error": error_msg})
                    continue

                if not newsletter_content_markdown:
                    error_msg = "Gemini returned empty content"
                    logger.warning(error_msg, user_email=user_email)
                    errors.append({"email": user_email, "error": error_msg})
                    continue

                # Convert Markdown to HTML
                newsletter_content_html = markdown.markdown(newsletter_content_markdown)

                # Create and send email
                email_message = EmailMessage(
                    to=user_email,
                    subject='Your Daily News Digest',
                    html_body=newsletter_content_html,
                    from_email=sender_email
                )

                logger.info("Sending email", user_email=user_email)

                if smtp_provider.send_email(email_message):
                    sent_newsletters_count += 1
                    logger.info("Newsletter sent successfully", user_email=user_email)
                else:
                    error_msg = "SMTP send failed"
                    logger.error(error_msg, user_email=user_email)
                    errors.append({"email": user_email, "error": error_msg})

            except Exception as e:
                error_msg = f"Processing error: {str(e)}"
                logger.error(error_msg, user_email=user_email, error=str(e))
                errors.append({"email": user_email, "error": error_msg})

        # Mark articles as processed (only if not in test mode)
        if not test_email:
            article_ids = [a['_id'] for a in articles]
            articles_collection.update_many({'_id': {'$in': article_ids}}, {'$set': {'processed': True}})
            logger.info('Articles marked as processed', count=len(article_ids))

        result = {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "users_processed": len(users),
            "articles_available": len(articles),
            "newsletters_sent": sent_newsletters_count,
            "users_skipped": len(skipped_users),
            "errors": len(errors),
            "details": {
                "skipped": skipped_users,
                "errors": errors
            }
        }

        logger.info('Manual newsletter generation completed',
                   sent=sent_newsletters_count,
                   skipped=len(skipped_users),
                   errors=len(errors))

        return func.HttpResponse(
            json.dumps(result, indent=2),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        error_result = {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
        logger.error('Fatal error in manual newsletter generation', error=str(e))

        return func.HttpResponse(
            json.dumps(error_result, indent=2),
            mimetype="application/json",
            status_code=500
        )
