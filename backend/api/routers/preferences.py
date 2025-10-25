"""API routes for user preferences management."""

from datetime import time
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import structlog

from api.db.session import get_db
from api.db.models import User, UserPreference
from api.models.preference import PreferenceUpdate, PreferenceResponse
from api.utils.auth import get_current_user

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/preferences", tags=["preferences"])


@router.get("/me", response_model=PreferenceResponse)
async def get_my_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current user's preferences.

    Returns user preferences including delivery settings, content filters, and notifications.
    If user has no preferences yet, creates default preferences.
    """
    try:
        # Get or create preferences
        preferences = db.query(UserPreference).filter(
            UserPreference.user_id == current_user.id
        ).first()

        if not preferences:
            # Create default preferences
            preferences = UserPreference(user_id=current_user.id)
            db.add(preferences)
            db.commit()
            db.refresh(preferences)
            logger.info(f"Created default preferences for user {current_user.email}")

        # Convert time object to string for JSON
        response_data = {
            "subscribed_companies": preferences.subscribed_companies or [],
            "subscribed_industries": preferences.subscribed_industries or [],
            "subscribed_technologies": preferences.subscribed_technologies or [],
            "subscribed_people": preferences.subscribed_people or [],
            "digest_frequency": preferences.digest_frequency,
            "delivery_time": preferences.delivery_time.strftime("%H:%M:%S"),
            "timezone": preferences.timezone,
            "delivery_days": preferences.delivery_days or [1, 2, 3, 4, 5],
            "email_format": preferences.email_format,
            "article_count_per_digest": preferences.article_count_per_digest,
            "summary_style": preferences.summary_style,
            "notification_preferences": preferences.notification_preferences or {},
            "content_filters": preferences.content_filters or {},
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update current user's preferences.

    Only provided fields will be updated. Omitted fields remain unchanged.
    """
    try:
        # Get or create preferences
        preferences = db.query(UserPreference).filter(
            UserPreference.user_id == current_user.id
        ).first()

        if not preferences:
            preferences = UserPreference(user_id=current_user.id)
            db.add(preferences)

        # Update fields (only if provided)
        update_data = updates.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field == "delivery_time" and value is not None:
                # Convert string to time object
                parts = value.split(":")
                value = time(hour=int(parts[0]), minute=int(parts[1]))

            setattr(preferences, field, value)

        db.commit()
        db.refresh(preferences)

        logger.info(
            f"Updated preferences for user {current_user.email}",
            updated_fields=list(update_data.keys())
        )

        # Return updated preferences
        response_data = {
            "subscribed_companies": preferences.subscribed_companies or [],
            "subscribed_industries": preferences.subscribed_industries or [],
            "subscribed_technologies": preferences.subscribed_technologies or [],
            "subscribed_people": preferences.subscribed_people or [],
            "digest_frequency": preferences.digest_frequency,
            "delivery_time": preferences.delivery_time.strftime("%H:%M:%S"),
            "timezone": preferences.timezone,
            "delivery_days": preferences.delivery_days or [1, 2, 3, 4, 5],
            "email_format": preferences.email_format,
            "article_count_per_digest": preferences.article_count_per_digest,
            "summary_style": preferences.summary_style,
            "notification_preferences": preferences.notification_preferences or {},
            "content_filters": preferences.content_filters or {},
        }

        return PreferenceResponse(**response_data)

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating preferences: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )


@router.delete("/me/companies/{company}")
async def remove_company_subscription(
    company: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a company from subscribed companies."""
    try:
        preferences = db.query(UserPreference).filter(
            UserPreference.user_id == current_user.id
        ).first()

        if not preferences:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Preferences not found"
            )

        if preferences.subscribed_companies and company in preferences.subscribed_companies:
            preferences.subscribed_companies.remove(company)
            db.commit()
            logger.info(f"Removed company {company} for user {current_user.email}")
            return {"message": f"Removed {company} from subscriptions"}

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company {company} not found in subscriptions"
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error removing company subscription: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove company subscription"
        )


@router.post("/me/companies/{company}")
async def add_company_subscription(
    company: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a company to subscribed companies."""
    try:
        preferences = db.query(UserPreference).filter(
            UserPreference.user_id == current_user.id
        ).first()

        if not preferences:
            preferences = UserPreference(user_id=current_user.id)
            db.add(preferences)

        if not preferences.subscribed_companies:
            preferences.subscribed_companies = []

        if company not in preferences.subscribed_companies:
            preferences.subscribed_companies.append(company)
            db.commit()
            logger.info(f"Added company {company} for user {current_user.email}")
            return {"message": f"Added {company} to subscriptions"}

        return {"message": f"{company} already subscribed"}

    except Exception as e:
        db.rollback()
        logger.error(f"Error adding company subscription: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add company subscription"
        )
