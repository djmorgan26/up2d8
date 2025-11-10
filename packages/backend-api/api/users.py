import logging
from datetime import UTC, datetime

from auth import User, get_current_user
from dependencies import get_db_client  # Import the new dependency
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from shared.validation import TopicsListField, PreferencesField, TopicField

router = APIRouter(tags=["Users"])
logger = logging.getLogger(__name__)


class UserCreate(BaseModel):
    """Request model for creating a user."""
    topics: TopicsListField = Field(
        ...,
        examples=[["Technology", "Science", "Business"]]
    )


class UserUpdate(BaseModel):
    """Request model for updating user preferences."""
    topics: TopicsListField | None = Field(
        default=None,
        examples=[["AI", "Climate", "Space"]]
    )
    preferences: PreferencesField | None = Field(
        default=None,
        examples=[{"theme": "dark", "notifications": "enabled"}]
    )


class TopicManage(BaseModel):
    """Request model for adding/removing topics."""
    topic: TopicField = Field(
        ...,
        examples=["Artificial Intelligence"]
    )


class PreferencesUpdate(BaseModel):
    """Request model for updating only preferences."""
    preferences: PreferencesField = Field(
        ...,
        examples=[{"theme": "dark", "notifications": "enabled", "language": "en"}]
    )


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


@router.get("/api/users/me", status_code=status.HTTP_200_OK)
async def get_current_user_info(
    db=Depends(get_db_client), user: User = Depends(get_current_user)
):
    """
    Get the currently authenticated user's information.

    This endpoint uses the /me convention for getting current user data,
    which is clearer than requiring the user_id parameter.
    """
    users_collection = db.users
    user_id = user.sub

    user_data = users_collection.find_one({"user_id": user_id}, {"_id": 0})
    if not user_data:
        # User authenticated but not in database - return basic info
        logger.warning(f"Authenticated user {user_id} not found in database")
        return {
            "user_id": user_id,
            "email": user.email,
            "name": user.name,
            "topics": [],
            "preferences": {},
            "created_at": None
        }

    return user_data


@router.patch("/api/users/me/preferences", status_code=status.HTTP_200_OK)
async def update_user_preferences(
    preferences_update: PreferencesUpdate,
    db=Depends(get_db_client),
    user: User = Depends(get_current_user)
):
    """
    Update only the user's preferences without affecting topics.

    This allows granular control over preferences separate from topic management.
    """
    users_collection = db.users
    user_id = user.sub

    result = users_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {"preferences": preferences_update.preferences},
            "$currentDate": {"updated_at": True}
        }
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please create a user profile first."
        )

    logger.info(f"User {user_id} updated preferences")
    return {"message": "Preferences updated successfully.", "user_id": user_id}


@router.post("/api/users/me/topics", status_code=status.HTTP_200_OK)
async def add_topic(
    topic_data: TopicManage,
    db=Depends(get_db_client),
    user: User = Depends(get_current_user)
):
    """
    Add a single topic to the user's topic list.

    Topics are added using $addToSet to prevent duplicates.
    """
    users_collection = db.users
    user_id = user.sub

    result = users_collection.update_one(
        {"user_id": user_id},
        {
            "$addToSet": {"topics": topic_data.topic},
            "$currentDate": {"updated_at": True}
        }
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please create a user profile first."
        )

    logger.info(f"User {user_id} added topic: {topic_data.topic}")
    return {"message": f"Topic '{topic_data.topic}' added successfully.", "user_id": user_id}


@router.delete("/api/users/me/topics/{topic}", status_code=status.HTTP_200_OK)
async def remove_topic(
    topic: str,
    db=Depends(get_db_client),
    user: User = Depends(get_current_user)
):
    """
    Remove a single topic from the user's topic list.

    The topic is specified as a URL path parameter instead of request body
    since DELETE requests with bodies are not well-supported by all HTTP clients.
    """
    users_collection = db.users
    user_id = user.sub

    result = users_collection.update_one(
        {"user_id": user_id},
        {
            "$pull": {"topics": topic},
            "$currentDate": {"updated_at": True}
        }
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please create a user profile first."
        )

    logger.info(f"User {user_id} removed topic: {topic}")
    return {"message": f"Topic '{topic}' removed successfully.", "user_id": user_id}


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

    update_fields = {}
    if user_update.topics is not None:
        update_fields["topics"] = user_update.topics
    if user_update.preferences is not None:
        update_fields["preferences"] = user_update.preferences

    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update provided."
        )

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
    user_data = users_collection.find_one({"user_id": authenticated_user_id}, {"_id": 0})
    if not user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user_data


@router.delete("/api/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: str,
    db=Depends(get_db_client),
    user: User = Depends(get_current_user)
):
    """
    Delete a user account.

    SECURITY: Users can only delete their own account.
    The user_id parameter must match the authenticated user's ID.
    """
    users_collection = db.users
    authenticated_user_id = user.sub

    # Security check: users can only delete their own account
    if user_id != authenticated_user_id:
        logger.warning(
            f"User {authenticated_user_id} attempted to delete user {user_id}",
            extra={"authenticated_user": authenticated_user_id, "target_user": user_id}
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account."
        )

    result = users_collection.delete_one({"user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    logger.info(f"User {user_id} deleted their account")
    return {"message": "User account deleted successfully."}
