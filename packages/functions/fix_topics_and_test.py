#!/usr/bin/env python3
"""Fix user topics to match available articles and test."""
import os
import pymongo
from dotenv import load_dotenv
from shared.key_vault_client import get_secret_client

load_dotenv()

# Set required environment variables
os.environ['KEY_VAULT_URI'] = os.getenv('KEY-VAULT-URI')

# Get Cosmos DB connection from Key Vault
secret_client = get_secret_client()
cosmos_connection = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value

# Connect to database
client = pymongo.MongoClient(cosmos_connection)
db = client.up2d8

# Check current articles
print("Current unprocessed articles:")
print("=" * 80)
articles = list(db.articles.find({'processed': False}))
for article in articles:
    print(f"Title: {article.get('title', 'NO TITLE')}")
    print(f"Summary: {article.get('summary', 'NO SUMMARY')}")
    print()

# Update your user topics to include "AI" which matches the article
print("Updating davidjmorgan26@gmail.com topics to include 'AI'...")
result = db.users.update_one(
    {'email': 'davidjmorgan26@gmail.com'},
    {'$set': {'topics': ['technology', 'science', 'health', 'AI', 'artificial intelligence']}}
)

if result.modified_count > 0:
    print("✅ Topics updated successfully")
else:
    print("⚠️  Topics may already be set or user not found")

# Verify
user = db.users.find_one({'email': 'davidjmorgan26@gmail.com'})
print(f"\nUpdated topics: {user.get('topics', [])}")
print("=" * 80)
