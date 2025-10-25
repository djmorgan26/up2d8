"""
Feedback API endpoints for article rating and user preference learning.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import List
import structlog
import uuid

from api.db.session import get_db
from api.db.models import User, ArticleFeedback, Article, Digest, UserPreferenceProfile
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
    db: Session = Depends(get_db),
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
    user = db.query(User).filter(User.id == user_id).first()
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
    article = db.query(Article).filter(Article.id == article_id).first()
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
    existing_feedback = (
        db.query(ArticleFeedback)
        .filter(
            and_(
                ArticleFeedback.user_id == user_id,
                ArticleFeedback.article_id == article_id,
                ArticleFeedback.digest_id == actual_digest_id if actual_digest_id else ArticleFeedback.digest_id.is_(None),
            )
        )
        .first()
    )

    if existing_feedback:
        # Update existing feedback
        existing_feedback.feedback_type = feedback_type
        existing_feedback.feedback_source = "email"
        db.commit()
    else:
        # Create new feedback
        new_feedback = ArticleFeedback(
            id=str(uuid.uuid4()),
            user_id=user_id,
            article_id=article_id,
            digest_id=actual_digest_id,  # Use actual_digest_id (None for test digests)
            feedback_type=feedback_type,
            feedback_source="email",
        )
        db.add(new_feedback)
        db.commit()

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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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
    article = db.query(Article).filter(Article.id == str(feedback.article_id)).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Verify digest exists if provided
    if feedback.digest_id:
        digest = db.query(Digest).filter(Digest.id == str(feedback.digest_id)).first()
        if not digest:
            raise HTTPException(status_code=404, detail="Digest not found")
        if digest.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Digest does not belong to user")

    # Check if feedback already exists
    existing_feedback = (
        db.query(ArticleFeedback)
        .filter(
            and_(
                ArticleFeedback.user_id == current_user.id,
                ArticleFeedback.article_id == str(feedback.article_id),
                ArticleFeedback.digest_id == str(feedback.digest_id) if feedback.digest_id else ArticleFeedback.digest_id.is_(None),
            )
        )
        .first()
    )

    if existing_feedback:
        # Update existing feedback
        existing_feedback.feedback_type = feedback.feedback_type
        existing_feedback.feedback_text = feedback.feedback_text
        existing_feedback.feedback_source = feedback.feedback_source
        db.commit()
        db.refresh(existing_feedback)

        logger.info("Updated existing feedback", feedback_id=existing_feedback.id)

        # Trigger preference update
        _update_user_preferences_from_feedback(
            db, current_user.id, article, feedback.feedback_type
        )

        return existing_feedback

    # Create new feedback
    new_feedback = ArticleFeedback(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        article_id=str(feedback.article_id),
        digest_id=str(feedback.digest_id) if feedback.digest_id else None,
        feedback_type=feedback.feedback_type,
        feedback_text=feedback.feedback_text,
        feedback_source=feedback.feedback_source,
    )

    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)

    logger.info("Created new feedback", feedback_id=new_feedback.id)

    # Trigger preference update
    _update_user_preferences_from_feedback(
        db, current_user.id, article, feedback.feedback_type
    )

    return new_feedback


@router.get("/stats", response_model=FeedbackStats)
async def get_feedback_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = 30,
):
    """
    Get feedback statistics for the current user.

    Args:
        days: Number of days to look back (default: 30)
    """
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Count feedback by type
    feedback_counts = (
        db.query(
            ArticleFeedback.feedback_type,
            func.count(ArticleFeedback.id).label("count"),
        )
        .filter(
            and_(
                ArticleFeedback.user_id == current_user.id,
                ArticleFeedback.created_at >= cutoff,
            )
        )
        .group_by(ArticleFeedback.feedback_type)
        .all()
    )

    # Convert to dict
    counts = {feedback_type: count for feedback_type, count in feedback_counts}

    total_feedback = sum(counts.values())
    thumbs_up = counts.get("thumbs_up", 0)
    thumbs_down = counts.get("thumbs_down", 0)
    not_relevant = counts.get("not_relevant", 0)

    # Calculate rates
    total_articles_received = (
        db.query(func.count(Digest.id))
        .filter(
            and_(
                Digest.user_id == current_user.id,
                Digest.sent_at >= cutoff,
            )
        )
        .scalar()
        or 0
    )

    feedback_rate = (
        total_feedback / total_articles_received if total_articles_received > 0 else 0
    )
    positive_rate = thumbs_up / total_feedback if total_feedback > 0 else 0

    return FeedbackStats(
        total_feedback=total_feedback,
        thumbs_up=thumbs_up,
        thumbs_down=thumbs_down,
        not_relevant=not_relevant,
        feedback_rate=feedback_rate,
        positive_rate=positive_rate,
    )


@router.get("/preferences", response_model=UserPreferenceProfileResponse)
async def get_preference_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the learned preference profile for the current user.

    This shows which companies, industries, and topics the system has learned
    the user is interested in based on their feedback and engagement.
    """
    profile = (
        db.query(UserPreferenceProfile)
        .filter(UserPreferenceProfile.user_id == current_user.id)
        .first()
    )

    if not profile:
        # Create default profile if it doesn't exist
        profile = UserPreferenceProfile(
            user_id=current_user.id,
            company_weights={},
            industry_weights={},
            topic_weights={},
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return profile


@router.get("/history", response_model=List[FeedbackResponse])
async def get_feedback_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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

    feedback_list = (
        db.query(ArticleFeedback)
        .filter(ArticleFeedback.user_id == current_user.id)
        .order_by(ArticleFeedback.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    return feedback_list


def _update_user_preferences_from_feedback(
    db: Session, user_id: str, article: Article, feedback_type: str
):
    """
    Update user preference profile based on feedback.

    When user gives thumbs up/down, extract signals and update preference weights.
    """
    # Get or create preference profile
    profile = (
        db.query(UserPreferenceProfile)
        .filter(UserPreferenceProfile.user_id == user_id)
        .first()
    )

    if not profile:
        profile = UserPreferenceProfile(
            user_id=user_id,
            company_weights={},
            industry_weights={},
            topic_weights={},
        )
        db.add(profile)

    # Update based on feedback type
    weight_delta = 0.1 if feedback_type == "thumbs_up" else -0.1

    # Update company weights
    if article.companies:
        company_weights = profile.company_weights or {}
        for company in article.companies:
            current_weight = company_weights.get(company, 0.5)  # Default neutral weight
            new_weight = max(0.0, min(1.0, current_weight + weight_delta))
            company_weights[company] = new_weight
        profile.company_weights = company_weights

    # Update industry weights
    if article.industries:
        industry_weights = profile.industry_weights or {}
        for industry in article.industries:
            current_weight = industry_weights.get(industry, 0.5)
            new_weight = max(0.0, min(1.0, current_weight + weight_delta))
            industry_weights[industry] = new_weight
        profile.industry_weights = industry_weights

    # Update topic weights (from categories)
    if article.categories:
        topic_weights = profile.topic_weights or {}
        for topic in article.categories:
            current_weight = topic_weights.get(topic, 0.5)
            new_weight = max(0.0, min(1.0, current_weight + weight_delta))
            topic_weights[topic] = new_weight
        profile.topic_weights = topic_weights

    # Update metrics
    profile.total_feedback_count += 1
    if feedback_type == "thumbs_up":
        profile.positive_feedback_count += 1
    elif feedback_type == "thumbs_down":
        profile.negative_feedback_count += 1

    profile.last_updated_at = datetime.utcnow()

    db.commit()

    logger.info(
        "Updated user preference profile",
        user_id=user_id,
        feedback_type=feedback_type,
        total_feedback=profile.total_feedback_count,
    )
