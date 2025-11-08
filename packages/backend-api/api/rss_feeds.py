from fastapi import APIRouter, status, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
import uuid
from datetime import datetime, UTC
from dependencies import get_db_client

router = APIRouter()

class RssFeedCreate(BaseModel):
    url: HttpUrl
    category: str | None = None

class RssFeedUpdate(BaseModel):
    url: HttpUrl | None = None
    category: str | None = None

@router.post("/api/rss_feeds", status_code=status.HTTP_201_CREATED)
async def create_rss_feed(feed: RssFeedCreate, db=Depends(get_db_client)):
    rss_feeds_collection = db.rss_feeds
    feed_id = str(uuid.uuid4())
    new_feed = {
        "id": feed_id,
        "url": str(feed.url),
        "category": feed.category,
        "created_at": datetime.now(UTC)
    }
    rss_feeds_collection.insert_one(new_feed)
    return {"message": "RSS Feed created successfully.", "id": feed_id}

@router.get("/api/rss_feeds", status_code=status.HTTP_200_OK)
async def get_rss_feeds(db=Depends(get_db_client)):
    rss_feeds_collection = db.rss_feeds
    feeds = list(rss_feeds_collection.find({}, {"_id": 0}))
    return feeds

@router.get("/api/rss_feeds/{feed_id}", status_code=status.HTTP_200_OK)
async def get_rss_feed(feed_id: str, db=Depends(get_db_client)):
    rss_feeds_collection = db.rss_feeds
    feed = rss_feeds_collection.find_one({"id": feed_id}, {"_id": 0})
    if not feed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RSS Feed not found.")
    return feed

@router.put("/api/rss_feeds/{feed_id}", status_code=status.HTTP_200_OK)
async def update_rss_feed(feed_id: str, feed_update: RssFeedUpdate, db=Depends(get_db_client)):
    rss_feeds_collection = db.rss_feeds
    
    update_fields = {}
    if feed_update.url is not None:
        update_fields["url"] = str(feed_update.url)
    if feed_update.category is not None:
        update_fields["category"] = feed_update.category

    if not update_fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update provided.")

    result = rss_feeds_collection.update_one(
        {"id": feed_id},
        {"$set": update_fields, "$currentDate": {"updated_at": True}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RSS Feed not found.")

    return {"message": "RSS Feed updated successfully."}

@router.delete("/api/rss_feeds/{feed_id}", status_code=status.HTTP_200_OK)
async def delete_rss_feed(feed_id: str, db=Depends(get_db_client)):
    rss_feeds_collection = db.rss_feeds
    result = rss_feeds_collection.delete_one({"id": feed_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RSS Feed not found.")
    return {"message": "RSS Feed deleted successfully."}
