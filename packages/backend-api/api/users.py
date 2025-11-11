from datetime import UTC, datetime
import logging

from auth import User, get_current_user
from dependencies import get_db_client  # Import the new dependency
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Users"])


class UserCreate(BaseModel):
    topics: list[str]


class UserUpdate(BaseModel):
    topics: list[str] | None = None
    preferences: dict | None = None


@router.post("/api/users", status_code=status.HTTP_200_OK)
async def create_user(
    user_create: UserCreate, db=Depends(get_db_client), user: User = Depends(get_current_user)
):
    users_collection = db.users
    user_id = user.sub
    email = user.email

    # Check if email is available from token
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not available in user token. Please ensure the 'email' scope is included.",
        )

    existing_user_by_id = users_collection.find_one({"user_id": user_id})

    if existing_user_by_id:
        # User exists and is correctly identified by user_id
        users_collection.update_one(
            {"user_id": user_id}, {"$addToSet": {"topics": {"$each": user_create.topics}}}
        )
        message = "User topics updated."
    else:
        # User not found by user_id, try to find by email
        existing_user_by_email = users_collection.find_one({"email": email})
        if existing_user_by_email:
            # User exists but is missing user_id, so we link it
            users_collection.update_one(
                {"email": email},
                {
                    "$set": {"user_id": user_id, "email": email},  # Ensure email is consistent
                    "$addToSet": {"topics": {"$each": user_create.topics}},
                },
            )
            message = "User account linked and topics updated."
        else:
            # This is a completely new user
            new_user = {
                "user_id": user_id,
                "email": email,
                "topics": user_create.topics,
                "created_at": datetime.now(UTC),
            }
            users_collection.insert_one(new_user)
            message = "New user created."

    return {"message": message, "user_id": user_id}


@router.put("/api/users/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    db=Depends(get_db_client),
    user: User = Depends(get_current_user),
):
    """
    Update user preferences and topics.
    Note: user_id parameter is kept for backwards compatibility but ignored.
    The authenticated user from the token is always used.
    """
    users_collection = db.users
    # Use the authenticated user's ID from the token, not the URL parameter
    authenticated_user_id = user.sub
    user_email = user.email

    update_fields = {}
    if user_update.topics is not None:
        update_fields["topics"] = user_update.topics
    if user_update.preferences is not None:
        # Use dot notation to update nested preference fields without replacing the entire object
        for key, value in user_update.preferences.items():
            update_fields[f"preferences.{key}"] = value

    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update provided."
        )

    # Try to update by user_id first
    result = users_collection.update_one(
        {"user_id": authenticated_user_id},
        {"$set": update_fields, "$currentDate": {"updated_at": True}},
    )

    # If not found by user_id, try by email and link the account
    if result.matched_count == 0 and user_email:
        # Detect OAuth provider from token issuer
        oauth_provider = "unknown"
        if hasattr(user, 'iss'):
            if 'microsoft' in user.iss or 'login.microsoftonline' in user.iss:
                oauth_provider = "entra_id"
            elif 'google' in user.iss or 'accounts.google' in user.iss:
                oauth_provider = "google"

        # First link the OAuth account
        link_result = users_collection.update_one(
            {"email": user_email},
            {"$set": {"user_id": authenticated_user_id, "oauth_provider": oauth_provider, "oauth_id": authenticated_user_id}}
        )
        if link_result.matched_count > 0:
            # Now update with the requested fields
            result = users_collection.update_one(
                {"user_id": authenticated_user_id},
                {"$set": update_fields, "$currentDate": {"updated_at": True}},
            )

    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return {"message": "Preferences updated.", "user_id": authenticated_user_id}


@router.get("/api/users/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(
    user_id: str, db=Depends(get_db_client), user: User = Depends(get_current_user)
):
    """
    Get user information.
    Note: user_id parameter is kept for backwards compatibility but ignored.
    The authenticated user from the token is always used.
    """
    users_collection = db.users
    # Use the authenticated user's ID from the token, not the URL parameter
    authenticated_user_id = user.sub
    user_email = user.email

    # Debug logging
    logger.info(f"GET /api/users - Token claims: sub={user.sub}, oid={user.oid}, email={user_email}, iss={user.iss}")
    logger.info(f"GET /api/users - Looking up user_id: {authenticated_user_id}")

    # Try to find by user_id first
    user_data = users_collection.find_one({"user_id": authenticated_user_id}, {"_id": 0})
    logger.info(f"GET /api/users - Found by user_id: {bool(user_data)}")

    # If not found by user_id, try to find by email (for OAuth users linking to email/password accounts)
    if not user_data and user_email:
        logger.info(f"GET /api/users - Trying lookup by email: {user_email}")
        user_data = users_collection.find_one({"email": user_email}, {"_id": 0})
        logger.info(f"GET /api/users - Found by email: {bool(user_data)}")

        # If found by email, update the user_id to link the OAuth account
        if user_data:
            logger.info(f"GET /api/users - Database user_id: {user_data.get('user_id')}, Token sub: {user.sub}")
            # Detect OAuth provider from token issuer
            oauth_provider = "unknown"
            if user.iss:
                logger.info(f"GET /api/users - Detected issuer: {user.iss}")
                if 'microsoft' in user.iss.lower() or 'login.microsoftonline' in user.iss.lower():
                    oauth_provider = "entra_id"
                elif 'google' in user.iss.lower() or 'accounts.google' in user.iss.lower():
                    oauth_provider = "google"

            logger.info(f"GET /api/users - Linking account: oauth_provider={oauth_provider}")
            users_collection.update_one(
                {"email": user_email},
                {"$set": {"user_id": authenticated_user_id, "oauth_provider": oauth_provider, "oauth_id": authenticated_user_id}}
            )
            # Refetch to get updated data
            user_data = users_collection.find_one({"user_id": authenticated_user_id}, {"_id": 0})
            logger.info(f"GET /api/users - After linking, found user: {bool(user_data)}")

    if not user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user_data


@router.delete("/api/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id: str, db=Depends(get_db_client)):
    users_collection = db.users
    result = users_collection.delete_one({"user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return {"message": "User deleted."}
