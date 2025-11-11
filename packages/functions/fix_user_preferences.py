#!/usr/bin/env python3
"""Fix user preferences format in database."""
import os
import pymongo
from dotenv import load_dotenv
from shared.key_vault_client import get_secret_client

load_dotenv()

# Set required environment variables from .env
os.environ['KEY_VAULT_URI'] = os.getenv('KEY-VAULT-URI')

# Get Cosmos DB connection from Key Vault
secret_client = get_secret_client()
cosmos_connection = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value

# Connect to database
client = pymongo.MongoClient(cosmos_connection)
db = client.up2d8
users_collection = db.users

print("Fixing user preferences format...")
print("=" * 80)

# Find users with incorrect preferences format
users = list(users_collection.find())

for user in users:
    email = user.get('email', 'NO EMAIL')
    prefs = user.get('preferences', {})

    # Check if preferences is not a dict (e.g., string)
    if not isinstance(prefs, dict):
        print(f"\nFixing user: {email}")
        print(f"  Current preferences: {prefs} (type: {type(prefs).__name__})")

        # Create proper preferences dict
        new_prefs = {
            'email_notifications': True,  # Enable by default
            'newsletter_frequency': 'daily',  # Daily by default
            'newsletter_format': prefs if isinstance(prefs, str) else 'concise'  # Use old value if it was a string
        }

        print(f"  New preferences: {new_prefs}")

        # Update the user
        result = users_collection.update_one(
            {'_id': user['_id']},
            {'$set': {'preferences': new_prefs}}
        )

        if result.modified_count > 0:
            print(f"  ✅ Updated successfully")
        else:
            print(f"  ❌ Update failed")

    elif prefs == {}:
        print(f"\nUser {email} has empty preferences, setting defaults...")
        new_prefs = {
            'email_notifications': True,
            'newsletter_frequency': 'daily',
            'newsletter_format': 'concise'
        }

        result = users_collection.update_one(
            {'_id': user['_id']},
            {'$set': {'preferences': new_prefs}}
        )

        if result.modified_count > 0:
            print(f"  ✅ Set default preferences")

    else:
        # Check if required keys are present
        required_keys = ['email_notifications', 'newsletter_frequency', 'newsletter_format']
        missing_keys = [key for key in required_keys if key not in prefs]

        if missing_keys:
            print(f"\nUser {email} missing keys: {missing_keys}")
            updates = {}
            if 'email_notifications' not in prefs:
                updates['preferences.email_notifications'] = True
            if 'newsletter_frequency' not in prefs:
                updates['preferences.newsletter_frequency'] = 'daily'
            if 'newsletter_format' not in prefs:
                updates['preferences.newsletter_format'] = 'concise'

            result = users_collection.update_one(
                {'_id': user['_id']},
                {'$set': updates}
            )

            if result.modified_count > 0:
                print(f"  ✅ Added missing keys")

print("\n" + "=" * 80)
print("Done! Verifying changes...")
print("=" * 80)

# Verify
users = list(users_collection.find())
for user in users:
    email = user.get('email', 'NO EMAIL')
    prefs = user.get('preferences', {})
    print(f"\nUser: {email}")
    print(f"  Email notifications: {prefs.get('email_notifications', 'MISSING')}")
    print(f"  Newsletter frequency: {prefs.get('newsletter_frequency', 'MISSING')}")
    print(f"  Newsletter format: {prefs.get('newsletter_format', 'MISSING')}")

print("\n" + "=" * 80)
