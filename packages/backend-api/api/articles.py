from fastapi import APIRouter, status, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
import uuid
from datetime import datetime, UTC
from dependencies import get_db_client

router = APIRouter()

class ArticleCreate(BaseModel):
    title: str
    link: HttpUrl
    summary: str
    published: str
    tags: list[str] = []
    source: str = "rss"  # rss, intelligent_crawler, manual
    content: str | None = None  # Full content for crawled articles

@router.post("/api/articles", status_code=status.HTTP_201_CREATED)
async def create_article(article: ArticleCreate, db=Depends(get_db_client)):
    """Create a new article. Used by Azure Functions for scraped content."""
    articles_collection = db.articles

    # Check for duplicates
    existing = articles_collection.find_one({"link": str(article.link)})
    if existing:
        return {
            "message": "Article already exists.",
            "id": existing.get("id", str(existing.get("_id")))
        }

    article_id = str(uuid.uuid4())
    new_article = {
        "id": article_id,
        "title": article.title,
        "link": str(article.link),
        "summary": article.summary,
        "published": article.published,
        "tags": article.tags,
        "source": article.source,
        "content": article.content,
        "processed": False,
        "created_at": datetime.now(UTC)
    }

    articles_collection.insert_one(new_article)

    # Log analytics event for article creation
    analytics_collection = db.analytics
    analytics_collection.insert_one({
        "user_id": "system",
        "event_type": "article_scraped",
        "details": {
            "article_id": article_id,
            "source": article.source,
            "tags": article.tags
        },
        "timestamp": datetime.now(UTC)
    })

    return {"message": "Article created successfully.", "id": article_id}

@router.get("/api/articles", status_code=status.HTTP_200_OK)
async def get_articles(db=Depends(get_db_client)):
    articles_collection = db.articles
    articles = list(articles_collection.find({}, {"_id": 0}))
    return articles

@router.get("/api/articles/{article_id}", status_code=status.HTTP_200_OK)
async def get_article(article_id: str, db=Depends(get_db_client)):
    articles_collection = db.articles
    article = articles_collection.find_one({"id": article_id}, {"_id": 0})
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found.")
    return article
