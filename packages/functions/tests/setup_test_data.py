import os
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Add the project root to sys.path to enable module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pymongo
from shared.key_vault_client import get_secret_client

def setup_test_data():
    """Set up test data for newsletter testing."""
    load_dotenv()
    print("=" * 80)
    print("SETTING UP TEST DATA FOR NEWSLETTER")
    print("=" * 80)
    print()

    try:
        # Get configuration
        secret_client = get_secret_client()
        cosmos_db_connection_string = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value

        # Connect to Cosmos DB
        client = pymongo.MongoClient(cosmos_db_connection_string)
        db = client.up2d8
        users_collection = db.users
        articles_collection = db.articles

        print("[1/4] Connected to Cosmos DB ✓")
        print()

        # Get test email from user
        test_email = input("Enter your email address for testing: ").strip()
        if not test_email:
            print("Error: Email is required")
            return

        # Check if user exists
        existing_user = users_collection.find_one({"email": test_email})

        if existing_user:
            print(f"[2/4] Found existing user: {test_email}")
            print(f"      Current topics: {existing_user.get('topics', [])}")
            print(f"      Current preferences: {existing_user.get('preferences', {})}")

            update_user = input("\n      Update this user's settings? (y/n): ").lower() == 'y'

            if update_user:
                # Update user with test-friendly settings
                users_collection.update_one(
                    {"email": test_email},
                    {
                        "$set": {
                            "topics": ["AI", "technology", "startup", "business", "innovation"],
                            "preferences": {
                                "email_notifications": True,
                                "newsletter_frequency": "daily",
                                "newsletter_format": "concise",
                                "breaking_news": False
                            },
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                print("      User updated ✓")
            else:
                print("      Keeping existing user settings")
        else:
            print(f"[2/4] Creating new test user: {test_email}")

            # Create test user
            test_user = {
                "user_id": f"test-{test_email}",
                "email": test_email,
                "topics": ["AI", "technology", "startup", "business", "innovation"],
                "preferences": {
                    "email_notifications": True,
                    "newsletter_frequency": "daily",
                    "newsletter_format": "concise",
                    "breaking_news": False
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            users_collection.insert_one(test_user)
            print("      User created ✓")

        print()

        # Create/update test articles
        print("[3/4] Setting up test articles...")

        # Reset some existing articles to unprocessed if they exist
        reset_count = articles_collection.update_many(
            {},
            {"$set": {"processed": False}}
        ).modified_count

        if reset_count > 0:
            print(f"      Reset {reset_count} articles to unprocessed ✓")

        # Create sample articles if needed
        article_count = articles_collection.count_documents({})

        if article_count < 5:
            print(f"      Only {article_count} articles found. Creating sample articles...")

            sample_articles = [
                {
                    "title": "Breakthrough in AI Language Models: New Architecture Shows Promise",
                    "summary": "Researchers unveil a novel neural network architecture that achieves state-of-the-art results in natural language understanding with 50% fewer parameters.",
                    "url": "https://example.com/ai-breakthrough",
                    "source": "TechCrunch",
                    "published_date": datetime.utcnow() - timedelta(hours=2),
                    "processed": False,
                    "created_at": datetime.utcnow()
                },
                {
                    "title": "Startup Raises $100M to Revolutionize Cloud Infrastructure",
                    "summary": "A Y Combinator-backed startup secures major funding to build next-generation cloud infrastructure focused on sustainability and cost reduction.",
                    "url": "https://example.com/startup-funding",
                    "source": "VentureBeat",
                    "published_date": datetime.utcnow() - timedelta(hours=5),
                    "processed": False,
                    "created_at": datetime.utcnow()
                },
                {
                    "title": "How Technology is Transforming Modern Business Operations",
                    "summary": "Industry experts discuss the impact of automation, AI, and digital transformation on traditional business models and operational efficiency.",
                    "url": "https://example.com/tech-business",
                    "source": "Harvard Business Review",
                    "published_date": datetime.utcnow() - timedelta(hours=8),
                    "processed": False,
                    "created_at": datetime.utcnow()
                },
                {
                    "title": "Innovation in Renewable Energy: Solar Efficiency Reaches New Heights",
                    "summary": "Scientists develop new solar panel technology that achieves 45% efficiency, a significant leap from current commercial panels at 20-25%.",
                    "url": "https://example.com/solar-innovation",
                    "source": "MIT Technology Review",
                    "published_date": datetime.utcnow() - timedelta(hours=12),
                    "processed": False,
                    "created_at": datetime.utcnow()
                },
                {
                    "title": "AI Startup Ecosystem Thrives Despite Economic Headwinds",
                    "summary": "Analysis shows AI-focused startups continue to attract investor interest, with funding up 30% year-over-year despite broader tech slowdown.",
                    "url": "https://example.com/ai-ecosystem",
                    "source": "The Information",
                    "published_date": datetime.utcnow() - timedelta(hours=16),
                    "processed": False,
                    "created_at": datetime.utcnow()
                }
            ]

            articles_collection.insert_many(sample_articles)
            print(f"      Created {len(sample_articles)} sample articles ✓")
        else:
            print(f"      {article_count} articles available ✓")

        print()

        # Summary
        print("[4/4] Setup complete! Summary:")
        print()

        user = users_collection.find_one({"email": test_email}, {"_id": 0})
        unprocessed = articles_collection.count_documents({"processed": False})

        print(f"      User: {test_email}")
        print(f"      Topics: {user.get('topics', [])}")
        print(f"      Email notifications: {user.get('preferences', {}).get('email_notifications', True)}")
        print(f"      Newsletter frequency: {user.get('preferences', {}).get('newsletter_frequency', 'daily')}")
        print(f"      Unprocessed articles: {unprocessed}")
        print()

        print("=" * 80)
        print("✅ TEST DATA READY!")
        print("=" * 80)
        print()
        print("You can now test the newsletter by:")
        print("1. Running the manual trigger function")
        print("2. Waiting for the scheduled run at 14:00 UTC (9 AM EST)")
        print()
        print(f"Test command:")
        print(f"  curl 'https://<function-app>.azurewebsites.net/api/NewsletterGeneratorManual?code=<function-key>&email={test_email}'")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    setup_test_data()
