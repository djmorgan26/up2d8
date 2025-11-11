#!/usr/bin/env python3
"""Quick script to check newsletter setup in database."""
import os
import pymongo
from dotenv import load_dotenv
from shared.key_vault_client import get_secret_client
from datetime import datetime

load_dotenv()

# Set required environment variables from .env
os.environ['KEY_VAULT_URI'] = os.getenv('KEY-VAULT-URI')

# Get Cosmos DB connection from Key Vault
secret_client = get_secret_client()
cosmos_connection = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value

# Connect to database
client = pymongo.MongoClient(cosmos_connection)
db = client.up2d8

print("=" * 80)
print("NEWSLETTER SETUP CHECK")
print("=" * 80)

# Check users
print("\n1. USERS CHECK:")
users = list(db.users.find())
print(f"   Total users: {len(users)}")

for user in users:
    print(f"\n   User: {user.get('email', 'NO EMAIL')}")
    print(f"   - Topics: {user.get('topics', [])}")
    prefs = user.get('preferences', {})
    if isinstance(prefs, dict):
        print(f"   - Email notifications: {prefs.get('email_notifications', 'NOT SET')}")
        print(f"   - Newsletter frequency: {prefs.get('newsletter_frequency', 'NOT SET')}")
        print(f"   - Newsletter format: {prefs.get('newsletter_format', 'NOT SET')}")
    else:
        print(f"   - Preferences: {prefs} (INVALID FORMAT)")

# Check articles
print("\n2. ARTICLES CHECK:")
total_articles = db.articles.count_documents({})
unprocessed_articles = db.articles.count_documents({'processed': False})
print(f"   Total articles: {total_articles}")
print(f"   Unprocessed articles: {unprocessed_articles}")

if unprocessed_articles > 0:
    print("\n   Recent unprocessed articles:")
    for article in db.articles.find({'processed': False}).limit(3):
        print(f"   - {article.get('title', 'NO TITLE')}")
        print(f"     Summary: {article.get('summary', 'NO SUMMARY')[:100]}...")

# Check if newsletter should run today
print("\n3. SCHEDULE CHECK:")
now = datetime.utcnow()
print(f"   Current UTC time: {now}")
print(f"   Current day of week: {now.strftime('%A')}")
print(f"   Newsletter schedule: 9:00 AM UTC daily (cron: 0 0 9 * * *)")

print("\n" + "=" * 80)
print("DIAGNOSIS:")
print("=" * 80)

if len(users) == 0:
    print("❌ NO USERS FOUND - Newsletter will not send")
elif unprocessed_articles == 0:
    print("❌ NO UNPROCESSED ARTICLES - Newsletter will not send")
else:
    issues = []
    for user in users:
        prefs = user.get('preferences', {})
        if isinstance(prefs, dict):
            if not prefs.get('email_notifications', True):
                issues.append(f"User {user.get('email')} has email notifications disabled")
        if not user.get('topics', []):
            issues.append(f"User {user.get('email')} has no topics configured")

    if issues:
        print("⚠️  POTENTIAL ISSUES:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ Setup looks good - newsletter should send at next scheduled time")

print("=" * 80)
