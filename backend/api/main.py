"""
UP2D8 FastAPI Application
Main entry point for the API
"""
import os
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

# Import routers
from api.routers import auth, scraping

# Configure structured logging
logger = structlog.get_logger()

# Load environment variables
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:5173").split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events
    """
    # Startup
    print(f"🚀 UP2D8 API starting in {ENVIRONMENT} mode...")
    print(f"📍 Debug mode: {DEBUG}")

    yield

    # Shutdown
    print("👋 UP2D8 API shutting down...")


# Create FastAPI application
app = FastAPI(
    title="UP2D8 API",
    description="AI-Powered Industry Insight Platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    debug=DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all HTTP requests with timing information.
    """
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    # Log request details
    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration * 1000, 2),
        client_ip=request.client.host if request.client else None,
    )

    return response


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers
    """
    return {
        "status": "healthy",
        "service": "UP2D8 API",
        "version": "0.1.0",
        "environment": ENVIRONMENT,
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Welcome to UP2D8 API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(scraping.router)  # Tags already defined in router

# TODO: Add more routers as features are implemented
# app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
# app.include_router(digests.router, prefix="/api/v1/digests", tags=["Digests"])
# app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG,
        log_level="info" if not DEBUG else "debug",
    )
