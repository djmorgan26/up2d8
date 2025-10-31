"""API routes for user preferences management."""

from datetime import time, datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database
import structlog

from api.db.session import get_db
from api.db.models import Collections, UserPreferenceDocument
from api.models.preference import PreferenceUpdate, PreferenceResponse
from api.utils.auth import get_current_user

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/preferences", tags=["preferences"])


@router.get("/me", response_model=PreferenceResponse)
async def get_my_preferences(
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    """
    Get current user's preferences.

    Returns user preferences including delivery settings, content filters, and notifications.
    If user has no preferences yet, creates default preferences.
    """
    try:
        # Get or create preferences
        prefs_collection = db[Collections.USER_PREFERENCES]
        preferences = prefs_collection.find_one({"user_id": current_user["id"]})

        if not preferences:
            # Create default preferences
            preferences = UserPreferenceDocument.create(user_id=current_user["id"])
            prefs_collection.insert_one(preferences)
            logger.info(f"Created default preferences for user {current_user['email']}")

        # Convert to response format
        response_data = {
            "subscribed_companies": preferences.get("subscribed_companies", []),
            "subscribed_industries": preferences.get("subscribed_industries", []),
            "subscribed_technologies": preferences.get("subscribed_technologies", []),
            "subscribed_people": preferences.get("subscribed_people", []),
            "digest_frequency": preferences.get("digest_frequency", "daily"),
            "delivery_time": preferences.get("delivery_time", "08:00:00"),
            "timezone": preferences.get("timezone", "America/New_York"),
            "delivery_days": preferences.get("delivery_days", [1, 2, 3, 4, 5]),
            "email_format": preferences.get("email_format", "html"),
            "article_count_per_digest": preferences.get("article_count_per_digest", 7),
            "summary_style": preferences.get("summary_style", "standard"),
            "notification_preferences": preferences.get("notification_preferences", {}),
            "content_filters": preferences.get("content_filters", {}),
        }

        return PreferenceResponse(**response_data)

    except Exception as e:
        logger.error(f"Error getting preferences: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get preferences"
        )


@router.put("/me", response_model=PreferenceResponse)
async def update_my_preferences(
    updates: PreferenceUpdate,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    """
    Update current user's preferences.

    Only provided fields will be updated. Omitted fields remain unchanged.
    """
    try:
        # Get or create preferences
        prefs_collection = db[Collections.USER_PREFERENCES]
        preferences = prefs_collection.find_one({"user_id": current_user["id"]})

        # Update fields (only if provided)
        update_data = updates.model_dump(exclude_unset=True)

        # Process updates
        update_dict = {"$set": {"updated_at": datetime.utcnow()}}

        for field, value in update_data.items():
            if value is not None:
                if field == "delivery_time":
                    # Keep as string in MongoDB
                    update_dict["$set"][field] = value
                else:
                    update_dict["$set"][field] = value

        if not preferences:
            # Create new preferences with updates
            new_prefs = UserPreferenceDocument.create(user_id=current_user["id"])
            for field, value in update_data.items():
                if value is not None:
                    new_prefs[field] = value
            prefs_collection.insert_one(new_prefs)
            preferences = new_prefs
            logger.info(
                f"Created preferences for user {current_user['email']}",
                updated_fields=list(update_data.keys())
            )
        else:
            # Update existing preferences
            prefs_collection.update_one(
                {"user_id": current_user["id"]},
                update_dict
            )
            # Fetch updated document
            preferences = prefs_collection.find_one({"user_id": current_user["id"]})
            logger.info(
                f"Updated preferences for user {current_user['email']}",
                updated_fields=list(update_data.keys())
            )

        # Return updated preferences
        response_data = {
            "subscribed_companies": preferences.get("subscribed_companies", []),
            "subscribed_industries": preferences.get("subscribed_industries", []),
            "subscribed_technologies": preferences.get("subscribed_technologies", []),
            "subscribed_people": preferences.get("subscribed_people", []),
            "digest_frequency": preferences.get("digest_frequency", "daily"),
            "delivery_time": preferences.get("delivery_time", "08:00:00"),
            "timezone": preferences.get("timezone", "America/New_York"),
            "delivery_days": preferences.get("delivery_days", [1, 2, 3, 4, 5]),
            "email_format": preferences.get("email_format", "html"),
            "article_count_per_digest": preferences.get("article_count_per_digest", 7),
            "summary_style": preferences.get("summary_style", "standard"),
            "notification_preferences": preferences.get("notification_preferences", {}),
            "content_filters": preferences.get("content_filters", {}),
        }

        return PreferenceResponse(**response_data)

    except Exception as e:
        logger.error(f"Error updating preferences: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )


@router.delete("/me/companies/{company}")
async def remove_company_subscription(
    company: str,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    """Remove a company from subscribed companies."""
    try:
        prefs_collection = db[Collections.USER_PREFERENCES]
        preferences = prefs_collection.find_one({"user_id": current_user["id"]})

        if not preferences:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Preferences not found"
            )

        subscribed_companies = preferences.get("subscribed_companies", [])
        if company in subscribed_companies:
            # Use MongoDB $pull operator to remove from array
            prefs_collection.update_one(
                {"user_id": current_user["id"]},
                {"$pull": {"subscribed_companies": company}}
            )
            logger.info(f"Removed company {company} for user {current_user['email']}")
            return {"message": f"Removed {company} from subscriptions"}

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company {company} not found in subscriptions"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing company subscription: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove company subscription"
        )


@router.post("/me/companies/{company}")
async def add_company_subscription(
    company: str,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    """Add a company to subscribed companies."""
    try:
        prefs_collection = db[Collections.USER_PREFERENCES]
        preferences = prefs_collection.find_one({"user_id": current_user["id"]})

        if not preferences:
            # Create new preferences with company
            new_prefs = UserPreferenceDocument.create(user_id=current_user["id"])
            new_prefs["subscribed_companies"] = [company]
            prefs_collection.insert_one(new_prefs)
            logger.info(f"Created preferences and added company {company} for user {current_user['email']}")
            return {"message": f"Added {company} to subscriptions"}

        subscribed_companies = preferences.get("subscribed_companies", [])
        if company not in subscribed_companies:
            # Use MongoDB $addToSet to add unique value to array
            prefs_collection.update_one(
                {"user_id": current_user["id"]},
                {"$addToSet": {"subscribed_companies": company}}
            )
            logger.info(f"Added company {company} for user {current_user['email']}")
            return {"message": f"Added {company} to subscriptions"}

        return {"message": f"{company} already subscribed"}

    except Exception as e:
        logger.error(f"Error adding company subscription: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add company subscription"
        )
