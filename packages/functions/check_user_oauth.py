#!/usr/bin/env python3
"""Check user OAuth configuration."""
import os, pymongo
from dotenv import load_dotenv
from shared.key_vault_client import get_secret_client

load_dotenv()
os.environ['KEY_VAULT_URI'] = os.getenv('KEY-VAULT-URI')
secret_client = get_secret_client()
conn = secret_client.get_secret('COSMOS-DB-CONNECTION-STRING-UP2D8').value
client = pymongo.MongoClient(conn)
db = client.up2d8

print("=" * 80)
print("USER AUTHENTICATION CHECK")
print("=" * 80)

users = list(db.users.find({'email': 'davidjmorgan26@gmail.com'}))

if not users:
    print("❌ No user found with email davidjmorgan26@gmail.com")
else:
    for user in users:
        print(f"\nUser found:")
        print(f"  Email: {user.get('email')}")
        print(f"  user_id: {user.get('user_id', 'NOT SET')}")
        print(f"  id: {user.get('id', 'NOT SET')}")
        print(f"  OAuth provider: {user.get('oauth_provider', 'NOT SET')}")
        print(f"  OAuth ID: {user.get('oauth_id', 'NOT SET')}")
        print(f"  Topics: {user.get('topics', [])}")
        print(f"  Preferences: {user.get('preferences', {})}")

print("\n" + "=" * 80)
print("DIAGNOSIS:")
print("=" * 80)
print("""
The frontend uses Google OAuth which provides a 'sub' claim as the user_id.
The backend API looks up users by 'user_id' field.

If you're logging in with Google OAuth, your OAuth 'sub' must match the 'user_id'
in the database.

Current issue: You likely have a user created via email/password with one user_id,
but are logging in via Google OAuth with a different user_id (sub).

Solution: We need to either:
1. Add your Google OAuth sub as the user_id to your existing account
2. Or create a new account via OAuth and migrate your data
3. Or link your OAuth account to your existing email/password account
""")
print("=" * 80)
