import uuid
from datetime import UTC, datetime
import logging
import json

import feedparser
from dependencies import get_db_client, get_gemini_api_key
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, HttpUrl
from google import genai
from google.genai import types

router = APIRouter(tags=["RSS Feeds"])
logger = logging.getLogger(__name__)

# Define a set of standard categories for normalization
STANDARD_CATEGORIES = {
    "Technology": ["technology", "tech news", "innovation", "gadgets", "technology news"],
    "News": ["news", "general news", "current events", "breaking news"],
    "Sports": ["sports", "athletics", "gaming"],
    "Business": ["business", "finance", "economy"],
    "Science": ["science", "research", "discovery"],
    "Entertainment": ["entertainment", "movies", "music", "pop culture"],
    "Lifestyle": ["lifestyle", "health", "wellness", "travel", "food"],
    "Programming": ["programming", "coding", "software development", "web development"],
    "Art": ["art", "design", "culture"],
    "Education": ["education", "learning", "academic"]
}

def standardize_category(raw_category: str | None) -> str:
    if not raw_category:
        return "Uncategorized"
    
    # Clean and normalize the raw category
    cleaned_category = raw_category.strip().lower()

    # Attempt to match against standard categories
    for standard_cat, synonyms in STANDARD_CATEGORIES.items():
        if cleaned_category == standard_cat.lower() or cleaned_category in synonyms:
            return standard_cat # Return the standardized, regular capitalized name

    return raw_category.strip() # Return original if no match


class RssFeedCreate(BaseModel):
    url: HttpUrl
    category: str | None = None
    title: str | None = None


class RssFeedUpdate(BaseModel):
    url: HttpUrl | None = None
    category: str | None = None
    title: str | None = None


class RssFeedSuggestRequest(BaseModel):
    query: str


@router.post("/api/rss_feeds", status_code=status.HTTP_201_CREATED)
async def create_rss_feed(feed: RssFeedCreate, db=Depends(get_db_client)):
    rss_feeds_collection = db.rss_feeds
    feed_id = str(uuid.uuid4())

    feed_title = feed.title # Prioritize title from the request
    if not feed_title: # If title not provided, try to fetch it
        try:
            parsed_feed = feedparser.parse(str(feed.url))
            if parsed_feed.feed and hasattr(parsed_feed.feed, "title"):
                feed_title = parsed_feed.feed.title
        except Exception as e:
            logger.warning(f"Failed to fetch feed title for {feed.url}: {e}")
            feed_title = "Untitled Feed" # Fallback if fetching fails
    
    if not feed_title: # Final fallback if title is still empty
        feed_title = "Untitled Feed"

    standardized_category = standardize_category(feed.category)

    new_feed = {
        "id": feed_id,
        "url": str(feed.url),
        "title": feed_title,
        "category": standardized_category,
        "created_at": datetime.now(UTC),
    }
    rss_feeds_collection.insert_one(new_feed)
    return {"message": "RSS Feed created successfully.", "id": feed_id}


@router.post("/api/rss_feeds/suggest", status_code=status.HTTP_200_OK)
async def suggest_rss_feeds(request: RssFeedSuggestRequest, api_key: str = Depends(get_gemini_api_key)):
    """
    Suggest RSS feeds based on a user query using Google Gemini and Google Search grounding.
    """
    try:
        client = genai.Client(api_key=api_key)

        system_instruction = """
        You are an AI assistant specialized in finding and suggesting RSS feeds.
        Your goal is to help users discover relevant RSS feeds based on their queries.

        Instructions:
        - Use Google Search to find RSS feed URLs, titles, and a suitable category related to the user's query.
        - Prioritize official or well-known sources.
        - For each suggestion, provide the feed title, its URL, and a concise category (e.g., "Technology", "News", "Sports", "Cooking").
        - Format your response as a JSON array of objects, where each object has 'title', 'url', and 'category' keys.
        - If no relevant RSS feeds are found, return an empty JSON array.
        - Example format: [{"title": "TechCrunch", "url": "https://techcrunch.com/feed/", "category": "Technology"}]
        """

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )

        # The prompt should clearly ask the LLM to find RSS feeds and format the output
        llm_prompt = f"Find RSS feeds related to: {request.query}. Provide the results as a JSON array of objects with 'title', 'url', and 'category' keys."

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=llm_prompt,
            config=config
        )

        # Attempt to parse the LLM's response as JSON
        try:
            response_text = response.text.strip()
            # Remove markdown code block fences if present
            if response_text.startswith("```json") and response_text.endswith("```"):
                response_text = response_text[len("```json"):-len("```")].strip()
            
            suggestions = json.loads(response_text)
            if not isinstance(suggestions, list):
                raise ValueError("LLM response is not a JSON array.")
            for item in suggestions:
                if not isinstance(item, dict) or "title" not in item or "url" not in item or "category" not in item:
                    raise ValueError("LLM response array items are not correctly formatted (missing title, url, or category).")
        except json.JSONDecodeError:
            logger.warning(f"LLM response was not valid JSON: {response.text}")
            suggestions = []
        except ValueError as ve:
            logger.warning(f"LLM response parsing error: {ve}. Response: {response.text}")
            suggestions = []

        return {
            "status": "success",
            "suggestions": suggestions
        }
    except Exception as e:
        logger.error(f"Gemini API error in suggest_rss_feeds: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Gemini API error: {e}"
        )


@router.get("/api/rss_feeds", status_code=status.HTTP_200_OK)
async def get_rss_feeds(db=Depends(get_db_client)):
    rss_feeds_collection = db.rss_feeds
    feeds = list(rss_feeds_collection.find({}, {"_id": 0}))
    return {"data": feeds}


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
    if feed_update.title is not None:
        update_fields["title"] = feed_update.title

    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update provided."
        )

    result = rss_feeds_collection.update_one(
        {"id": feed_id}, {"$set": update_fields, "$currentDate": {"updated_at": True}}
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
