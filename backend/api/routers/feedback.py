"""
Feedback API endpoints for article rating and user preference learning.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from pymongo.database import Database
from datetime import datetime, timedelta
from typing import List
import structlog
import uuid

from api.db.session import get_db
from api.db.cosmos_db import CosmosCollections
# User is dict type from get_current_user
from api.models.feedback import (
    FeedbackCreate,
    FeedbackResponse,
    FeedbackStats,
    UserPreferenceProfileResponse,
)
from api.utils.auth import get_current_user
from api.services.analytics_tracker import get_analytics_tracker

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/feedback", tags=["feedback"])


@router.get("/track")
async def track_feedback_from_email(
    article_id: str,
    user_id: str,
    type: str,
    digest_id: str = None,
    db: Database = Depends(get_db),
):
    """
    Track feedback from email link clicks (no authentication required).

    This endpoint is called when users click thumbs up/down buttons in their email.
    It returns a simple HTML thank you page.
    """
    logger.info(
        "Tracking feedback from email",
        user_id=user_id,
        article_id=article_id,
        feedback_type=type,
    )

    # Verify user exists
    user = db[CosmosCollections.USERS].find_one({"id": user_id})
    if not user:
        return HTMLResponse(
            content="""
            <html>
                <head><title>UP2D8 Feedback</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h2>❌ Invalid Link</h2>
                    <p>This feedback link is invalid or expired.</p>
                </body>
            </html>
            """,
            status_code=404,
        )

    # Verify article exists
    article = db[CosmosCollections.ARTICLES].find_one({"id": article_id})
    if not article:
        return HTMLResponse(
            content="""
            <html>
                <head><title>UP2D8 Feedback</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h2>❌ Article Not Found</h2>
                    <p>This article no longer exists.</p>
                </body>
            </html>
            """,
            status_code=404,
        )

    # Map type to feedback_type
    feedback_type = type.replace("thumbs_", "") if type.startswith("thumbs_") else type
    if feedback_type not in ["up", "down"]:
        feedback_type = "not_relevant"

    # Convert to proper format
    if feedback_type == "up":
        feedback_type = "thumbs_up"
    elif feedback_type == "down":
        feedback_type = "thumbs_down"

    # Handle test digest_id (set to None for test digests)
    actual_digest_id = None if digest_id == "test" else digest_id

    # Check if feedback already exists
    feedback_query = {
        "user_id": user_id,
        "article_id": article_id,
    }
    if actual_digest_id:
        feedback_query["digest_id"] = actual_digest_id
    else:
        feedback_query["digest_id"] = None

    existing_feedback = db[CosmosCollections.ARTICLE_FEEDBACK].find_one(feedback_query)

    if existing_feedback:
        # Update existing feedback
        db[CosmosCollections.ARTICLE_FEEDBACK].update_one(
            {"id": existing_feedback["id"]},
            {"$set": {
                "feedback_type": feedback_type,
                "feedback_source": "email",
                "updated_at": datetime.utcnow(),
            }}
        )
    else:
        # Create new feedback
        new_feedback = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "article_id": article_id,
            "digest_id": actual_digest_id,
            "feedback_type": feedback_type,
            "feedback_source": "email",
            "created_at": datetime.utcnow(),
        }
        db[CosmosCollections.ARTICLE_FEEDBACK].insert_one(new_feedback)

    # Update user preferences
    _update_user_preferences_from_feedback(db, user_id, article, feedback_type)

    # Track analytics
    analytics_tracker = get_analytics_tracker(db)
    analytics_tracker.track_feedback(article_id, user_id, feedback_type)

    # Return thank you page
    emoji = "👍" if feedback_type == "thumbs_up" else "👎"
    message = "Thanks for your feedback!" if feedback_type == "thumbs_up" else "Thanks! We'll show you less content like this."

    return HTMLResponse(
        content=f"""
        <html>
            <head>
                <title>UP2D8 Feedback Received</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; text-align: center; padding: 50px; background-color: #f5f5f7;">
                <div style="max-width: 500px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="font-size: 64px; margin-bottom: 20px;">{emoji}</div>
                    <h2 style="color: #1d1d1f; margin-bottom: 10px;">Feedback Received</h2>
                    <p style="color: #6e6e73; font-size: 16px;">{message}</p>
                    <p style="color: #6e6e73; font-size: 14px; margin-top: 20px;">
                        Your preferences help us personalize future digests for you.
                    </p>
                    <div style="margin-top: 30px;">
                        <a href="https://up2d8.ai" style="display: inline-block; padding: 12px 24px; background-color: #667eea; color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">
                            Return to UP2D8
                        </a>
                    </div>
                </div>
            </body>
        </html>
        """,
        status_code=200,
    )


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback: FeedbackCreate,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    """
    Submit feedback on an article.

    This feedback is used to:
    - Learn user preferences over time
    - Improve article recommendations
    - Calculate engagement metrics
    """
    logger.info(
        "Creating feedback",
        user_id=current_user.id,
        article_id=str(feedback.article_id),
        feedback_type=feedback.feedback_type,
    )

    # Verify article exists
    article = db[CosmosCollections.ARTICLES].find_one({"id": str(feedback.article_id)})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Verify digest exists if provided
    if feedback.digest_id:
        digest = db[CosmosCollections.DIGESTS].find_one({"id": str(feedback.digest_id)})
        if not digest:
            raise HTTPException(status_code=404, detail="Digest not found")
        if digest["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Digest does not belong to user")

    # Check if feedback already exists
    feedback_query = {
        "user_id": current_user["id"],
        "article_id": str(feedback.article_id),
    }
    if feedback.digest_id:
        feedback_query["digest_id"] = str(feedback.digest_id)
    else:
        feedback_query["digest_id"] = None

    existing_feedback = db[CosmosCollections.ARTICLE_FEEDBACK].find_one(feedback_query)

    if existing_feedback:
        # Update existing feedback
        db[CosmosCollections.ARTICLE_FEEDBACK].update_one(
            {"id": existing_feedback["id"]},
            {"$set": {
                "feedback_type": feedback.feedback_type,
                "feedback_text": feedback.feedback_text,
                "feedback_source": feedback.feedback_source,
                "updated_at": datetime.utcnow(),
            }}
        )
        # Fetch updated document
        updated_feedback = db[CosmosCollections.ARTICLE_FEEDBACK].find_one(
            {"id": existing_feedback["id"]}
        )

        logger.info("Updated existing feedback", feedback_id=updated_feedback["id"])

        # Trigger preference update
        _update_user_preferences_from_feedback(
            db, current_user["id"], article, feedback.feedback_type
        )

        return FeedbackResponse(**updated_feedback)

    # Create new feedback
    new_feedback = {
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "article_id": str(feedback.article_id),
        "digest_id": str(feedback.digest_id) if feedback.digest_id else None,
        "feedback_type": feedback.feedback_type,
        "feedback_text": feedback.feedback_text,
        "feedback_source": feedback.feedback_source,
        "created_at": datetime.utcnow(),
    }

    db[CosmosCollections.ARTICLE_FEEDBACK].insert_one(new_feedback)

    logger.info("Created new feedback", feedback_id=new_feedback["id"])

    # Trigger preference update
    _update_user_preferences_from_feedback(
        db, current_user["id"], article, feedback.feedback_type
    )

    return FeedbackResponse(**new_feedback)


@router.get("/stats", response_model=FeedbackStats)
async def get_feedback_stats(
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db),
    days: int = 30,
):
    """
    Get feedback statistics for the current user.

    Args:
        days: Number of days to look back (default: 30)
    """
    logger.info(
        "Getting feedback stats",
        user_id=current_user["id"],
        days=days,
    )

    # Calculate cutoff date
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # MongoDB aggregation pipeline to count feedback by type
    pipeline = [
        {
            "$match": {
                "user_id": current_user["id"],
                "created_at": {"$gte": cutoff_date}
            }
        },
        {
            "$group": {
                "_id": "$feedback_type",
                "count": {"$sum": 1}
            }
        }
    ]

    results = list(db[CosmosCollections.ARTICLE_FEEDBACK].aggregate(pipeline))

    # Parse results
    thumbs_up = 0
    thumbs_down = 0
    not_relevant = 0

    for result in results:
        feedback_type = result["_id"]
        count = result["count"]

        if feedback_type == "thumbs_up":
            thumbs_up = count
        elif feedback_type == "thumbs_down":
            thumbs_down = count
        elif feedback_type == "not_relevant":
            not_relevant = count

    total_feedback = thumbs_up + thumbs_down + not_relevant

    # Calculate rates
    feedback_rate = 0.0
    positive_rate = 0.0

    if total_feedback > 0:
        # Feedback rate is percentage of positive feedback out of total
        positive_rate = (thumbs_up / total_feedback) * 100

        # Get total articles delivered in this period for feedback_rate
        # Count articles in digests sent to this user
        digests_sent = db[CosmosCollections.DIGESTS].count_documents({
            "user_id": current_user["id"],
            "sent_at": {"$gte": cutoff_date}
        })

        if digests_sent > 0:
            # Rough estimate: assume 7 articles per digest
            articles_delivered = digests_sent * 7
            feedback_rate = (total_feedback / articles_delivered) * 100

    return FeedbackStats(
        total_feedback=total_feedback,
        thumbs_up=thumbs_up,
        thumbs_down=thumbs_down,
        not_relevant=not_relevant,
        feedback_rate=round(feedback_rate, 2),
        positive_rate=round(positive_rate, 2),
    )


@router.get("/preferences", response_model=UserPreferenceProfileResponse)
async def get_preference_profile(
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    """
    Get the learned preference profile for the current user.

    This shows which companies, industries, and topics the system has learned
    the user is interested in based on their feedback and engagement.
    """
    profile = db[CosmosCollections.USER_PREFERENCE_PROFILES].find_one(
        {"user_id": current_user["id"]}
    )

    if not profile:
        # Create default profile if it doesn't exist
        profile = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "company_weights": {},
            "industry_weights": {},
            "topic_weights": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        db[CosmosCollections.USER_PREFERENCE_PROFILES].insert_one(profile)

    return UserPreferenceProfileResponse(**profile)


@router.get("/history", response_model=List[FeedbackResponse])
async def get_feedback_history(
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    """
    Get feedback history for the current user.

    Args:
        limit: Maximum number of feedback items to return (default: 50, max: 100)
        offset: Number of items to skip (for pagination)
    """
    if limit > 100:
        limit = 100

    feedback_list = list(
        db[CosmosCollections.ARTICLE_FEEDBACK]
        .find({"user_id": current_user["id"]})
        .sort("created_at", -1)
        .skip(offset)
        .limit(limit)
    )

    return [FeedbackResponse(**feedback) for feedback in feedback_list]


def _update_user_preferences_from_feedback(
    db: Database, user_id: str, article: dict, feedback_type: str
):
    """
    Update user preference profile based on feedback.

    When user gives thumbs up/down, extract signals and update preference weights.

    TODO: Implement MongoDB version with proper update operations
    For now, this is a stub to prevent import errors.
    """
    logger.info(
        "User preference update (stub - TODO: implement MongoDB version)",
        user_id=user_id,
        feedback_type=feedback_type,
    )
