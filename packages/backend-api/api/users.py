from datetime import UTC, datetime

from auth import User, get_current_user
from dependencies import get_db_client  # Import the new dependency
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

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
async def update_user(user_id: str, user_update: UserUpdate, db=Depends(get_db_client)):
    users_collection = db.users

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
        {"user_id": user_id}, {"$set": update_fields, "$currentDate": {"updated_at": True}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return {"message": "Preferences updated."}


@router.get("/api/users/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(user_id: str, db=Depends(get_db_client)):
    users_collection = db.users
    user = users_collection.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


@router.delete("/api/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id: str, db=Depends(get_db_client)):
    users_collection = db.users
    result = users_collection.delete_one({"user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return {"message": "User deleted."}
