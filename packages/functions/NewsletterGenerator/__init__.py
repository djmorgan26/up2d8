import os
import pymongo
import google.generativeai as genai
import azure.functions as func
import markdown # Import the markdown library
from shared.email_service import EmailMessage, SMTPProvider
from shared.embeddings_service import EmbeddingsService
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

        # Initialize embeddings service for semantic search
        embeddings_service = EmbeddingsService(api_key=gemini_api_key)

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
        user_articles_collection = db.user_articles

        # Fetch users and all unsent articles (not limited by 'processed' flag)
        users = list(users_collection.find())
        # Get recent articles (e.g., from last 7 days) instead of using 'processed' flag
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        articles = list(articles_collection.find({
            'created_at': {'$gte': week_ago}
        }))

        if not articles:
            logger.info("No new articles to process.")
            return

        sent_newsletters_count = 0
        for user in users:
            try:
                user_id = user.get('user_id')
                user_email = user.get('email')

                if not user_id:
                    logger.warning("User missing user_id", user_email=user_email)
                    continue

                # Get user topics and preferences (new schema)
                user_topics = user.get('topics', [])
                user_preferences = user.get('preferences', {})

                # Get newsletter settings
                newsletter_format = user_preferences.get('newsletter_format', 'concise')
                newsletter_frequency = user_preferences.get('newsletter_frequency', 'daily')
                email_notifications = user_preferences.get('email_notifications', True)

                # Check if user has email notifications enabled
                if not email_notifications:
                    logger.info("Email notifications disabled for user", user_email=user_email)
                    continue

                # Check if newsletter should be sent based on frequency
                if not should_send_newsletter(newsletter_frequency):
                    logger.info("Skipping user due to frequency setting",
                               user_email=user_email,
                               frequency=newsletter_frequency)
                    continue

                # Get articles already sent to this user
                sent_article_ids = set()
                user_articles = user_articles_collection.find({
                    'user_id': user_id,
                    'sent_in_newsletter': True
                }, {'article_id': 1})
                for ua in user_articles:
                    sent_article_ids.add(ua.get('article_id'))

                # Filter out already-sent articles
                unsent_articles = [a for a in articles if a.get('id') not in sent_article_ids]

                if not unsent_articles:
                    logger.info("No unsent articles for user",
                              user_email=user_email,
                              sent_count=len(sent_article_ids))
                    continue

                # Generate or retrieve topic embeddings
                # Check if user has topic_embeddings cached in DB
                topic_embeddings = user.get('topic_embeddings', [])

                # If not cached or topics changed, regenerate
                if not topic_embeddings or len(topic_embeddings) != len(user_topics):
                    logger.info("Generating topic embeddings",
                              user_email=user_email,
                              topics=user_topics)
                    topic_embeddings = []
                    for topic in user_topics:
                        emb = embeddings_service.generate_embedding(topic)
                        if emb:
                            topic_embeddings.append(emb)

                    # Cache embeddings in user document
                    if topic_embeddings:
                        users_collection.update_one(
                            {'user_id': user_id},
                            {'$set': {'topic_embeddings': topic_embeddings}}
                        )

                if not topic_embeddings:
                    logger.warning("No topic embeddings available for user",
                                 user_email=user_email)
                    continue

                # Rank articles by semantic similarity + recency
                ranked_articles = embeddings_service.rank_articles_by_topics(
                    articles=unsent_articles,
                    topic_embeddings=topic_embeddings,
                    recency_weight=0.3
                )

                # Filter by minimum similarity threshold and limit to top N
                MIN_SIMILARITY = 0.3  # Only include articles with >30% similarity
                MAX_ARTICLES = 15  # Limit newsletter to 15 articles

                relevant_articles = [
                    article for article, score in ranked_articles
                    if score >= MIN_SIMILARITY
                ][:MAX_ARTICLES]

                if not relevant_articles:
                    logger.info("No semantically relevant articles for user",
                              user_email=user_email,
                              topics=user_topics,
                              unsent_count=len(unsent_articles))
                    continue

                logger.info("Selected articles for user",
                          user_email=user_email,
                          article_count=len(relevant_articles),
                          top_score=ranked_articles[0][1] if ranked_articles else 0.0)

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
                    logger.info("Newsletter sent",
                              user_email=user_email,
                              article_count=len(relevant_articles))

                    # Mark articles as sent for this user
                    for article in relevant_articles:
                        article_id = article.get('id')
                        if article_id:
                            try:
                                user_articles_collection.update_one(
                                    {
                                        'user_id': user_id,
                                        'article_id': article_id
                                    },
                                    {
                                        '$set': {
                                            'sent_in_newsletter': True,
                                            'sent_at': datetime.utcnow()
                                        },
                                        '$setOnInsert': {
                                            'user_id': user_id,
                                            'article_id': article_id,
                                            'read': False,
                                            'bookmarked': False,
                                            'created_at': datetime.utcnow()
                                        }
                                    },
                                    upsert=True
                                )
                            except Exception as e:
                                logger.error("Failed to track article for user",
                                           user_id=user_id,
                                           article_id=article_id,
                                           error=str(e))
                else:
                    logger.error("Failed to send newsletter", user_email=user_email)

            except Exception as e:
                logger.error("Error processing user", user_email=user_email, error=str(e))

        # No longer need to mark articles as globally processed
        logger.info('Newsletter generation complete',
                   sent_count=sent_newsletters_count,
                   total_users=len(users))

        logger.info('Sent newsletters', count=sent_newsletters_count)

    except Exception as e:
        logger.error('An error occurred in NewsletterGenerator', error=str(e))

    logger.info('NewsletterGenerator function execution finished.')
