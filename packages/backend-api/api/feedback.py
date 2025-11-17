"""
Feedback API endpoints for article ratings and user engagement.
"""
from datetime import UTC, datetime
import logging

from dependencies import get_db_client
from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Feedback"])


class FeedbackCreate(BaseModel):
    message_id: str
    user_id: str
    rating: str


class ArticleFeedback(BaseModel):
    article_id: str
    rating: str  # "up" or "down"
    comment: str | None = None


# Helper functions for HTML responses (defined before use)
def get_success_html(rating: str) -> str:
    """Generate success HTML page for feedback submission."""
    emoji = "👍" if rating == "up" else "👎"
    message = "marked as helpful" if rating == "up" else "marked as not relevant"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Feedback Received - Up2D8</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .container {{
                background: white;
                border-radius: 16px;
                padding: 48px 32px;
                max-width: 500px;
                margin: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
            }}
            .emoji {{
                font-size: 64px;
                margin-bottom: 24px;
            }}
            h1 {{
                color: #1f2937;
                margin: 0 0 16px 0;
                font-size: 28px;
            }}
            p {{
                color: #6b7280;
                font-size: 16px;
                line-height: 1.6;
                margin: 0 0 32px 0;
            }}
            .button {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 14px 32px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
                transition: transform 0.2s;
            }}
            .button:hover {{
                transform: translateY(-2px);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="emoji">{emoji}</div>
            <h1>Thank You!</h1>
            <p>Your feedback has been recorded. This article has been {message}.</p>
            <p>We'll use this to improve your personalized news experience.</p>
            <a href="https://gray-wave-00bdfc60f.3.azurestaticapps.net" class="button">
                Back to Up2D8
            </a>
        </div>
    </body>
    </html>
    """


def get_error_html(error_message: str) -> str:
    """Generate error HTML page."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Error - Up2D8</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .container {{
                background: white;
                border-radius: 16px;
                padding: 48px 32px;
                max-width: 500px;
                margin: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
            }}
            .emoji {{
                font-size: 64px;
                margin-bottom: 24px;
            }}
            h1 {{
                color: #1f2937;
                margin: 0 0 16px 0;
                font-size: 28px;
            }}
            p {{
                color: #6b7280;
                font-size: 16px;
                line-height: 1.6;
                margin: 0 0 32px 0;
            }}
            .button {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 14px 32px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="emoji">❌</div>
            <h1>Oops!</h1>
            <p>{error_message}</p>
            <a href="https://gray-wave-00bdfc60f.3.azurestaticapps.net" class="button">
                Back to Up2D8
            </a>
        </div>
    </body>
    </html>
    """


# Route handlers
@router.post("/api/feedback", status_code=status.HTTP_201_CREATED)
async def create_feedback(feedback: FeedbackCreate, db=Depends(get_db_client)):
    """Legacy feedback endpoint for chat messages."""
    feedback_collection = db.feedback
    feedback_entry = {
        "message_id": feedback.message_id,
        "user_id": feedback.user_id,
        "rating": feedback.rating,
        "timestamp": datetime.now(UTC),
    }
    feedback_collection.insert_one(feedback_entry)
    return {"message": "Feedback received."}


@router.get("/api/feedback", status_code=status.HTTP_200_OK)
async def submit_article_feedback_via_get(
    article: str = Query(..., description="Article ID"),
    rating: str = Query(..., description="Rating: 'up' or 'down'"),
    user_id: str = Query(None, description="User ID (optional for anonymous feedback)"),
    db=Depends(get_db_client)
):
    """
    Submit article feedback via GET request (for email links).

    This endpoint allows feedback submission through simple email links like:
    /api/feedback?article=123&rating=up&user_id=456

    Returns an HTML page thanking the user.
    """
    feedback_collection = db.article_feedback

    # Validate rating
    if rating not in ["up", "down"]:
        return HTMLResponse(
            content=get_error_html("Invalid rating. Must be 'up' or 'down'."),
            status_code=400
        )

    # Create feedback document
    feedback_doc = {
        "article_id": article,
        "rating": rating,
        "created_at": datetime.now(UTC),
        "source": "email"
    }

    if user_id:
        feedback_doc["user_id"] = user_id
        # Upsert feedback (one rating per user per article)
        feedback_collection.update_one(
            {"user_id": user_id, "article_id": article},
            {"$set": feedback_doc},
            upsert=True
        )
    else:
        # Anonymous feedback, just insert
        feedback_collection.insert_one(feedback_doc)

    logger.info(
        "Email feedback submitted",
        user_id=user_id,
        article_id=article,
        rating=rating
    )

    # Return HTML page
    return HTMLResponse(content=get_success_html(rating))

