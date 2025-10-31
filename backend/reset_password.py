#!/usr/bin/env python3
"""Reset user password in MongoDB"""
import asyncio
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def reset_password():
    # Connect to MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
    client = AsyncIOMotorClient(mongodb_url)
    db = client.up2d8

    email = "davidjmorgan26@gmail.com"
    new_password = "password12345"

    # Hash the new password
    password_hash = pwd_context.hash(new_password)

    # Update the user's password
    result = await db.users.update_one(
        {"email": email},
        {"$set": {"password_hash": password_hash}}
    )

    if result.modified_count > 0:
        print(f"✅ Password reset successful for {email}")
        print(f"New password: {new_password}")
    else:
        print(f"❌ User not found: {email}")

    client.close()

if __name__ == "__main__":
    asyncio.run(reset_password())
