from fastapi import APIRouter, status, HTTPException, Depends
from pydantic import BaseModel, EmailStr
import uuid
from datetime import datetime, UTC
from dependencies import get_db_client # Import the new dependency

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    topics: list[str]

class UserUpdate(BaseModel):
    topics: list[str] | None = None
    preferences: dict | None = None

@router.post("/api/users", status_code=status.HTTP_200_OK)
async def create_user(user: UserCreate, db=Depends(get_db_client)):
    users_collection = db.users
    existing_user = users_collection.find_one({"email": user.email})

    if existing_user:
        # Update existing user's topics
        users_collection.update_one(
            {"email": user.email},
            {"$addToSet": {"topics": {"$each": user.topics}}}
        )
        user_id = existing_user["user_id"]
        message = "User already exists, topics updated."
    else:
        # Create new user
        user_id = str(uuid.uuid4())
        new_user = {
            "user_id": user_id,
            "email": user.email,
            "topics": user.topics,
            "created_at": datetime.now(UTC)
        }
        users_collection.insert_one(new_user)
        message = "Subscription confirmed."

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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update provided.")

    result = users_collection.update_one(
        {"user_id": user_id},
        {"$set": update_fields, "$currentDate": {"updated_at": True}}
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
