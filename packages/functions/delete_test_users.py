#!/usr/bin/env python3
"""
Admin script to delete test users from the database.
Run this from Azure Cloud Shell or any environment with access to Key Vault.
"""
import os
import pymongo
from shared.key_vault_client import get_secret_client

def main():
    # Get MongoDB connection
    secret_client = get_secret_client()
    cosmos_connection = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value

    client = pymongo.MongoClient(cosmos_connection)
    db = client.up2d8

    # Show all users before deletion
    print("Current users in database:")
    for user in db.users.find({}, {"email": 1, "_id": 0}):
        print(f"  - {user.get('email')}")

    # Delete test users
    test_emails = ["test@example.com", "existing@example.com", "legacy@example.com"]
    result = db.users.delete_many({"email": {"$in": test_emails}})
    print(f"\nDeleted {result.deleted_count} test users: {test_emails}")

    # Show remaining users
    print("\nRemaining users in database:")
    for user in db.users.find({}, {"email": 1, "_id": 0}):
        print(f"  - {user.get('email')}")

    client.close()
    print("\nDone!")

if __name__ == "__main__":
    main()
