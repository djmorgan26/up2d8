from contextlib import asynccontextmanager
import logging

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
from logging_config import configure_logging
from middleware.logging_middleware import RequestLoggingMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Runs on startup:
    - Configure structured logging
    - Load Azure OpenID configuration
    """
    # Configure logging first
    configure_logging(log_level="INFO", enable_structured=True)
    logger.info("UP2D8 Backend API starting up")

    # Load Azure OpenID configuration
    await azure_scheme.openid_config.load_config()
    logger.info("Azure authentication configured")

    yield

    # Shutdown
    logger.info("UP2D8 Backend API shutting down")


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

# Request logging middleware (logs all requests/responses with timing)
# Exclude health check and root endpoints to reduce noise
app.add_middleware(
    RequestLoggingMiddleware,
    exclude_paths=["/", "/api/health"]
)

# CORS configuration
# Production: Specify exact origins for security
# Development: Use * for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local Vite dev server
        "http://localhost:8080",  # Local Vite alternative port
        "https://gray-wave-00bdfc60f.3.azurestaticapps.net",  # Production Static Web App
        # Add custom domain here if configured later
    ],
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
