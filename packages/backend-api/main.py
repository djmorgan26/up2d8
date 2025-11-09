from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import health, users, articles, chat, rss_feeds, analytics, feedback, auth as auth_routes
from auth import azure_scheme

app = FastAPI(title="UP2D8 Backend API", version="1.0.0")

# Initialize Azure AD authentication
azure_scheme.openid_config.load_config()  # type: ignore

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

@app.get("/")
async def root():
    return {
        "service": "UP2D8 Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }
