from contextlib import asynccontextmanager

from api import (
    analytics,
    articles,
    chat,
    feedback,
    health,
    rss_feeds,
    topics,
    users,
)
from api import (
    auth as auth_routes,
)
from auth import azure_scheme
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load the OpenID configuration on startup.
    """
    await azure_scheme.openid_config.load_config()
    yield


app = FastAPI(
    title="UP2D8 Backend API",
    version="1.0.0",
    description="Personal news digest and information management platform API",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "System", "description": "System health and monitoring endpoints"},
        {"name": "Authentication", "description": "User authentication and authorization"},
        {"name": "Users", "description": "User management and preferences"},
        {"name": "Articles", "description": "Article content management"},
        {"name": "RSS Feeds", "description": "RSS feed subscriptions and management"},
        {"name": "Topics", "description": "AI-powered topic discovery and suggestions"},
        {"name": "Chat", "description": "AI chat sessions and message history"},
        {"name": "Analytics", "description": "Event tracking and analytics"},
        {"name": "Feedback", "description": "User feedback collection"},
    ],
)

# CORS configuration for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(auth_routes.router)  # Add auth router
app.include_router(users.router)
app.include_router(articles.router)
app.include_router(chat.router)
app.include_router(rss_feeds.router)
app.include_router(analytics.router)
app.include_router(feedback.router)
app.include_router(topics.router)


@app.get("/")
async def root():
    return {
        "service": "UP2D8 Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }
