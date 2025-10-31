"""
Digest API endpoints for digest generation and email delivery.

Endpoints:
- POST /test - Send test digest to current user
- POST /generate - Generate digest for current user
- GET /history - Get digest history for current user
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pymongo.database import Database
from pydantic import BaseModel, EmailStr
from datetime import datetime
import structlog

from api.db.session import get_db
from api.db.cosmos_db import CosmosCollections
# User is dict type from get_current_user
from api.utils.auth import get_current_user
from workers.tasks.digests import send_test_digest, generate_user_digest

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/digests", tags=["digests"])


# ============================================================================
# Response Models
# ============================================================================


class DigestResponse(BaseModel):
    """Response model for digest information."""

    id: str
    user_id: str
    digest_date: str
    article_count: int
    personalized: bool
    sent_at: Optional[str]
    delivery_status: str
    delivery_error: Optional[str]

    class Config:
        from_attributes = True


class DigestTaskResponse(BaseModel):
    """Response model for digest generation task."""

    task_id: str
    user_id: str
    message: str


class TestDigestRequest(BaseModel):
    """Request model for test digest."""

    email: Optional[EmailStr] = None
    name: Optional[str] = None


class DigestHistoryResponse(BaseModel):
    """Response model for digest history."""

    total_count: int
    digests: List[DigestResponse]


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/test", response_model=DigestTaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def send_test_digest_endpoint(
    request: TestDigestRequest = TestDigestRequest(),
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    """
    Send a test digest to the current user or specified email.

    This endpoint triggers an async Celery task to generate and send a test digest.
    The test digest includes recent articles from high-authority sources.

    Args:
        request: Optional email and name for test digest
        current_user: Authenticated user
        db: Database session

    Returns:
        Task ID and status message
    """
    # Use current user's email if not specified
    email = request.email or current_user["email"]
    name = request.name or current_user.get("full_name") or "User"

    logger.info(
        f"Triggering test digest for {email}",
        user_id=current_user["id"],
        email=email,
    )

    # Queue the Celery task
    task = send_test_digest.delay(
        email,
        name,
    )

    return DigestTaskResponse(
        task_id=task.id,
        user_id=current_user["id"],
        message=f"Test digest generation queued for {email}. Check your email in a few moments.",
    )


@router.post("/generate", response_model=DigestTaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_digest_endpoint(
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    """
    Generate and send a personalized digest for the current user.

    This endpoint triggers an async Celery task to:
    1. Build a personalized digest based on user preferences
    2. Send the digest via email
    3. Create a digest record in the database

    Returns:
        Task ID and status message
    """
    logger.info(
        f"Triggering digest generation for user {current_user['id']}",
        email=current_user["email"],
    )

    # Queue the Celery task
    task = generate_user_digest.delay(user_id=current_user["id"])

    return DigestTaskResponse(
        task_id=task.id,
        user_id=current_user["id"],
        message=f"Digest generation queued for {current_user['email']}. Check your email in a few moments.",
    )


@router.get("/history", response_model=DigestHistoryResponse)
async def get_digest_history(
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db),
    limit: int = Query(default=30, le=100, description="Maximum number of digests to return"),
    offset: int = Query(default=0, ge=0, description="Number of digests to skip"),
):
    """
    Get digest history for the current user.

    Returns a paginated list of digests that have been sent to the user,
    including delivery status and article counts.

    Args:
        current_user: Authenticated user
        db: Database session
        limit: Maximum number of digests to return (max 100)
        offset: Number of digests to skip (for pagination)

    Returns:
        List of digest records with metadata
    """
    # Get total count
    total_count = db[CosmosCollections.DIGESTS].count_documents(
        {"user_id": current_user["id"]}
    )

    # Get paginated digests
    digests = list(
        db[CosmosCollections.DIGESTS]
        .find({"user_id": current_user["id"]})
        .sort("sent_at", -1)
        .skip(offset)
        .limit(limit)
    )

    logger.info(
        f"Retrieved {len(digests)} digests for user {current_user['id']}",
        total_count=total_count,
        limit=limit,
        offset=offset,
    )

    # Convert to DigestResponse objects
    digest_responses = [DigestResponse(**digest) for digest in digests]

    return DigestHistoryResponse(
        total_count=total_count,
        digests=digest_responses,
    )


@router.get("/{digest_id}", response_model=DigestResponse)
async def get_digest(
    digest_id: str,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    """
    Get details for a specific digest.

    Args:
        digest_id: UUID of the digest
        current_user: Authenticated user
        db: Database session

    Returns:
        Digest details

    Raises:
        404: Digest not found
        403: Digest does not belong to user
    """
    digest = db[CosmosCollections.DIGESTS].find_one({"id": digest_id})

    if not digest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Digest not found",
        )

    if digest["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Digest does not belong to user",
        )

    return DigestResponse(**digest)
