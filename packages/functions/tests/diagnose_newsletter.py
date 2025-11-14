import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Add the project root to sys.path to enable module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pymongo
from shared.key_vault_client import get_secret_client

def diagnose_newsletter_system():
    """Comprehensive diagnostic for newsletter delivery issues."""
    load_dotenv()
    print("=" * 80)
    print("NEWSLETTER SYSTEM DIAGNOSTIC")
    print("=" * 80)
    print()

    issues_found = []

    try:
        # 1. Get configuration
        print("[1/6] Checking configuration...")
        secret_client = get_secret_client()

        cosmos_db_connection_string = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value
        brevo_smtp_user = os.environ.get("BREVO_SMTP_USER")
        brevo_smtp_password = secret_client.get_secret("UP2D8-SMTP-KEY").value
        brevo_smtp_host = os.environ.get("BREVO_SMTP_HOST")
        brevo_smtp_port = os.environ.get("BREVO_SMTP_PORT")
        sender_email = os.environ.get("SENDER_EMAIL")

        print(f"   ✓ SMTP Host: {brevo_smtp_host}")
        print(f"   ✓ SMTP Port: {brevo_smtp_port}")
        print(f"   ✓ SMTP User: {brevo_smtp_user}")
        print(f"   ✓ Sender Email: {sender_email}")
        print(f"   ✓ SMTP Password: {'***' + brevo_smtp_password[-4:] if brevo_smtp_password else 'NOT SET'}")
        print()

        # 2. Connect to Cosmos DB
        print("[2/6] Connecting to Cosmos DB...")
        client = pymongo.MongoClient(cosmos_db_connection_string)
        db = client.up2d8
        users_collection = db.users
        articles_collection = db.articles
        print("   ✓ Connected successfully")
        print()

        # 3. Check users
        print("[3/6] Checking users in database...")
        total_users = users_collection.count_documents({})
        users_with_email_enabled = users_collection.count_documents({
            'preferences.email_notifications': True
        })
        users_with_daily_frequency = users_collection.count_documents({
            'preferences.newsletter_frequency': 'daily'
        })

        print(f"   Total users: {total_users}")
        print(f"   Users with email notifications enabled: {users_with_email_enabled}")
        print(f"   Users with daily frequency: {users_with_daily_frequency}")

        if total_users == 0:
            issues_found.append("⚠ NO USERS FOUND IN DATABASE")

        if users_with_email_enabled == 0:
            issues_found.append("⚠ NO USERS HAVE EMAIL NOTIFICATIONS ENABLED")

        print()

        # 4. Check user details
        print("[4/6] Checking user details...")
        users = list(users_collection.find({}, {'_id': 0, 'email': 1, 'topics': 1, 'preferences': 1}))
        for i, user in enumerate(users, 1):
            email = user.get('email', 'NO EMAIL')
            topics = user.get('topics', [])
            prefs = user.get('preferences', {})
            email_notif = prefs.get('email_notifications', 'NOT SET')
            frequency = prefs.get('newsletter_frequency', 'NOT SET')

            print(f"\n   User {i}: {email}")
            print(f"      Topics: {topics if topics else 'NONE'}")
            print(f"      Email notifications: {email_notif}")
            print(f"      Newsletter frequency: {frequency}")

            if not topics:
                issues_found.append(f"⚠ User {email} has NO TOPICS set")

            if email_notif is False:
                issues_found.append(f"⚠ User {email} has email notifications DISABLED")

        print()

        # 5. Check articles
        print("[5/6] Checking articles...")
        total_articles = articles_collection.count_documents({})
        unprocessed_articles = articles_collection.count_documents({'processed': False})
        processed_articles = articles_collection.count_documents({'processed': True})

        print(f"   Total articles: {total_articles}")
        print(f"   Unprocessed articles: {unprocessed_articles}")
        print(f"   Processed articles: {processed_articles}")

        if total_articles == 0:
            issues_found.append("⚠ NO ARTICLES IN DATABASE")

        if unprocessed_articles == 0:
            issues_found.append("⚠ NO UNPROCESSED ARTICLES (Newsletter will not send)")

        # Show sample unprocessed articles
        if unprocessed_articles > 0:
            print("\n   Sample unprocessed articles:")
            sample_articles = list(articles_collection.find({'processed': False}, {'_id': 0, 'title': 1}).limit(3))
            for article in sample_articles:
                print(f"      • {article.get('title', 'NO TITLE')}")

        print()

        # 6. Check newsletter schedule logic
        print("[6/6] Checking newsletter schedule logic...")
        today = datetime.utcnow()
        print(f"   Current UTC time: {today.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"   Current day of week: {today.strftime('%A')} (weekday {today.weekday()})")
        print(f"   Current day of month: {today.day}")
        print(f"   Schedule: 14:00 UTC (9 AM EST) daily")

        # Check if any daily users would receive newsletter
        would_send_count = 0
        for user in users:
            prefs = user.get('preferences', {})
            email_notif = prefs.get('email_notifications', True)
            frequency = prefs.get('newsletter_frequency', 'daily')
            topics = user.get('topics', [])

            should_send = False
            if email_notif:
                if frequency == 'daily':
                    should_send = True
                elif frequency == 'weekly' and today.weekday() == 0:
                    should_send = True
                elif frequency == 'monthly' and today.day == 1:
                    should_send = True

            if should_send and topics and unprocessed_articles > 0:
                would_send_count += 1

        print(f"\n   Users that WOULD receive newsletter today: {would_send_count}")

        if would_send_count == 0:
            issues_found.append("⚠ NO USERS WOULD RECEIVE NEWSLETTER TODAY")

        print()

    except Exception as e:
        print(f"   ✗ Error: {e}")
        issues_found.append(f"⚠ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

    # Summary
    print()
    print("=" * 80)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 80)

    if issues_found:
        print("\n❌ ISSUES FOUND:\n")
        for issue in issues_found:
            print(f"   {issue}")
        print()
        print("RECOMMENDATIONS:")
        print()

        if "NO USERS" in str(issues_found):
            print("   1. Create user accounts in the database")

        if "NO TOPICS" in str(issues_found):
            print("   2. Users need to set their topics via the web app preferences")

        if "email notifications DISABLED" in str(issues_found).lower():
            print("   3. Users need to enable email notifications in settings")

        if "NO UNPROCESSED ARTICLES" in str(issues_found):
            print("   4. Check if DailyArticleScraper is running and creating articles")
            print("      Or manually reset some articles: db.articles.update_many({}, {'$set': {'processed': false}})")

        if "NO ARTICLES" in str(issues_found):
            print("   5. Run DailyArticleScraper to populate articles")
    else:
        print("\n✅ NO ISSUES FOUND - System should be working!")
        print("\nPossible reasons for not receiving emails:")
        print("   1. Azure Function may not be deployed or running")
        print("   2. Check spam/junk folder")
        print("   3. Check Azure Function logs in Azure Portal")
        print("   4. Verify function schedule is correct (should run at 14:00 UTC)")

    print()
    print("=" * 80)

if __name__ == "__main__":
    diagnose_newsletter_system()
