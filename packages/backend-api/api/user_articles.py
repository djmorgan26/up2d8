"""
User-Article relationship tracking API.

Tracks which articles have been sent to users, read status, and bookmarks.
This replaces the global 'processed' flag with per-user tracking.
"""

import uuid
from datetime import UTC, datetime

from auth import User, get_current_user
from dependencies import get_db_client
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

router = APIRouter(tags=["User Articles"])


class UserArticleCreate(BaseModel):
    article_id: str
    sent_in_newsletter: bool = False
    read: bool = False
    bookmarked: bool = False


class UserArticleUpdate(BaseModel):
    read: bool | None = None
    bookmarked: bool | None = None


@router.post("/api/users/{user_id}/articles", status_code=status.HTTP_201_CREATED)
async def track_article_for_user(
    user_id: str,
    user_article: UserArticleCreate,
    db=Depends(get_db_client),
    user: User = Depends(get_current_user),
):
    """
    Track an article for a user (e.g., mark as sent in newsletter).
    Used by newsletter generation function.
    """
    user_articles_collection = db.user_articles

    # Check if relationship already exists
    existing = user_articles_collection.find_one(
        {"user_id": user_id, "article_id": user_article.article_id}
    )

    if existing:
        # Update existing record
        update_fields = {}
        if user_article.sent_in_newsletter:
            update_fields["sent_in_newsletter"] = True
            update_fields["sent_at"] = datetime.now(UTC)
        if user_article.read:
            update_fields["read"] = True
        if user_article.bookmarked:
            update_fields["bookmarked"] = True

        if update_fields:
            user_articles_collection.update_one(
                {"user_id": user_id, "article_id": user_article.article_id},
                {"$set": update_fields},
            )

        return {
            "message": "User article tracking updated.",
            "user_id": user_id,
            "article_id": user_article.article_id,
        }

    # Create new tracking record
    new_user_article = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "article_id": user_article.article_id,
        "sent_in_newsletter": user_article.sent_in_newsletter,
        "sent_at": datetime.now(UTC) if user_article.sent_in_newsletter else None,
        "read": user_article.read,
        "bookmarked": user_article.bookmarked,
        "created_at": datetime.now(UTC),
    }

    user_articles_collection.insert_one(new_user_article)

    return {
        "message": "User article tracking created.",
        "user_id": user_id,
        "article_id": user_article.article_id,
    }


@router.put("/api/users/{user_id}/articles/{article_id}", status_code=status.HTTP_200_OK)
async def update_user_article(
    user_id: str,
    article_id: str,
    user_article_update: UserArticleUpdate,
    db=Depends(get_db_client),
    user: User = Depends(get_current_user),
):
    """Update article read/bookmark status for a user."""
    user_articles_collection = db.user_articles

    # Verify user matches authenticated user
    if user_id != user.sub:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own article status.",
        )

    update_fields = {}
    if user_article_update.read is not None:
        update_fields["read"] = user_article_update.read
    if user_article_update.bookmarked is not None:
        update_fields["bookmarked"] = user_article_update.bookmarked

    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update provided."
        )

    # Upsert: create if doesn't exist, update if it does
    result = user_articles_collection.update_one(
        {"user_id": user_id, "article_id": article_id},
        {
            "$set": update_fields,
            "$setOnInsert": {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "article_id": article_id,
                "sent_in_newsletter": False,
                "sent_at": None,
                "created_at": datetime.now(UTC),
            },
        },
        upsert=True,
    )

    return {
        "message": "Article status updated.",
        "user_id": user_id,
        "article_id": article_id,
        "modified": result.modified_count > 0,
    }


@router.get("/api/users/{user_id}/articles/sent", status_code=status.HTTP_200_OK)
async def get_sent_articles_for_user(
    user_id: str, db=Depends(get_db_client), user: User = Depends(get_current_user)
):
    """Get list of article IDs that have been sent to this user in newsletters."""
    user_articles_collection = db.user_articles

    # Verify user matches authenticated user
    if user_id != user.sub:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own articles.",
        )

    sent_articles = list(
        user_articles_collection.find(
            {"user_id": user_id, "sent_in_newsletter": True}, {"article_id": 1, "_id": 0}
        )
    )

    return {"article_ids": [a["article_id"] for a in sent_articles]}


@router.get("/api/users/{user_id}/bookmarks", status_code=status.HTTP_200_OK)
async def get_bookmarked_articles(
    user_id: str, db=Depends(get_db_client), user: User = Depends(get_current_user)
):
    """Get full article details for bookmarked articles."""
    user_articles_collection = db.user_articles
    articles_collection = db.articles

    # Verify user matches authenticated user
    if user_id != user.sub:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own bookmarks.",
        )

    # Get bookmarked article IDs
    bookmarked = list(
        user_articles_collection.find(
            {"user_id": user_id, "bookmarked": True}, {"article_id": 1, "_id": 0}
        )
    )
    article_ids = [b["article_id"] for b in bookmarked]

    # Fetch full article details
    articles = list(articles_collection.find({"id": {"$in": article_ids}}, {"_id": 0}))

    # Transform to match frontend expectations
    transformed = []
    for article in articles:
        source = article.get("source")
        if not source or source == "rss":
            link = article.get("link", "")
            if link:
                from urllib.parse import urlparse

                domain = urlparse(link).netloc
                source = domain.replace("www.", "").split(".")[0].title() if domain else "RSS"
            else:
                source = "RSS"

        transformed.append(
            {
                "id": article.get("id"),
                "title": article.get("title"),
                "description": article.get("summary"),
                "url": article.get("link"),
                "published_at": article.get("published"),
                "source": source,
                "feed_id": article.get("feed_id"),
                "feed_name": article.get("feed_name"),
                "bookmarked": True,
            }
        )

    return {"data": transformed}


@router.get("/api/users/{user_id}/newsletters", status_code=status.HTTP_200_OK)
async def get_newsletter_history(
    user_id: str, db=Depends(get_db_client), user: User = Depends(get_current_user)
):
    """
    Get newsletter history for a user.
    Returns articles grouped by sent_at date.
    """
    user_articles_collection = db.user_articles
    articles_collection = db.articles

    # Verify user matches authenticated user
    if user_id != user.sub:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own newsletter history.",
        )

    # Get all articles sent in newsletters, sorted by date
    sent_articles = list(
        user_articles_collection.find(
            {"user_id": user_id, "sent_in_newsletter": True}, {"_id": 0}
        ).sort("sent_at", -1)
    )

    # Group by date
    newsletters_by_date = {}
    for ua in sent_articles:
        sent_date = ua.get("sent_at")
        if sent_date:
            date_key = sent_date.strftime("%Y-%m-%d")
            if date_key not in newsletters_by_date:
                newsletters_by_date[date_key] = []
            newsletters_by_date[date_key].append(ua["article_id"])

    # Fetch article details for each newsletter
    result = []
    for date_key, article_ids in newsletters_by_date.items():
        articles = list(articles_collection.find({"id": {"$in": article_ids}}, {"_id": 0}))

        # Transform articles
        transformed = []
        for article in articles:
            source = article.get("source")
            if not source or source == "rss":
                link = article.get("link", "")
                if link:
                    from urllib.parse import urlparse

                    domain = urlparse(link).netloc
                    source = (
                        domain.replace("www.", "").split(".")[0].title() if domain else "RSS"
                    )
                else:
                    source = "RSS"

            transformed.append(
                {
                    "id": article.get("id"),
                    "title": article.get("title"),
                    "description": article.get("summary"),
                    "url": article.get("link"),
                    "published_at": article.get("published"),
                    "source": source,
                    "feed_id": article.get("feed_id"),
                    "feed_name": article.get("feed_name"),
                }
            )

        result.append({"date": date_key, "articles": transformed})

    return {"newsletters": result}
