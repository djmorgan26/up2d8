import os
from dotenv import load_dotenv
from pymongo import MongoClient
import sys

# Add the backend-api directory to the Python path
backend_api_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'packages', 'backend-api'))
sys.path.insert(0, backend_api_path)

# Now import modules using their full path within the backend-api package
from api.rss_feeds import standardize_category, STANDARD_CATEGORIES
from shared.key_vault_client import KeyVaultClient

load_dotenv()

def get_db_client():
    connection_string = os.getenv("MONGODB_CONNECTION_STRING")
    
    if not connection_string:
        # Assuming KEY_VAULT_URI is set in .env for local dev
        kv_client = KeyVaultClient()
        try:
            connection_string = kv_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8")
        except Exception as e:
            print(f"Warning: Could not retrieve MongoDB connection from Key Vault: {e}")
            connection_string = "mongodb://localhost:27017/" # Fallback for local dev

    client = MongoClient(connection_string)
    database_name = os.getenv("MONGODB_DATABASE", "up2d8")
    return client[database_name]

def run_standardization():
    db = get_db_client()
    rss_feeds_collection = db.rss_feeds

    print("Starting category standardization for existing RSS feeds...")
    
    updated_count = 0
    for feed in rss_feeds_collection.find({}):
        original_category = feed.get("category")
        standardized_cat = standardize_category(original_category)

        # Only update if the category is actually different after standardization
        # This handles cases like "technology" -> "Technology"
        if original_category != standardized_cat:
            rss_feeds_collection.update_one(
                {"_id": feed["_id"]},
                {"$set": {"category": standardized_cat}}
            )
            print(f"Updated feed '{feed.get('title', feed.get('url'))}': '{original_category}' -> '{standardized_cat}'")
            updated_count += 1
        elif original_category is None and standardized_cat == "Uncategorized":
            # Handle case where original was None and now it's "Uncategorized"
            rss_feeds_collection.update_one(
                {"_id": feed["_id"]},
                {"$set": {"category": standardized_cat}}
            )
            print(f"Updated feed '{feed.get('title', feed.get('url'))}': 'None' -> '{standardized_cat}'")
            updated_count += 1
        elif original_category and original_category != standardized_cat:
            # Catch cases where original was not None, but not exactly the standardized form
            rss_feeds_collection.update_one(
                {"_id": feed["_id"]},
                {"$set": {"category": standardized_cat}}
            )
            print(f"Updated feed '{feed.get('title', feed.get('url'))}': '{original_category}' -> '{standardized_cat}'")
            updated_count += 1

    print(f"Category standardization complete. {updated_count} feeds updated.")

if __name__ == "__main__":
    run_standardization()