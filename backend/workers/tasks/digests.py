"""
Celery tasks for digest generation and delivery.

Tasks:
- send_test_digest: Send a test digest to a specific email
- generate_user_digest: Generate and send digest for one user
- generate_scheduled_digests: Generate digests for all users (scheduled)
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any
import structlog

from workers.celery_app import celery_app
from api.db.session import SessionLocal
from api.db.models import User, UserPreference
from api.services.digest_builder import get_digest_builder
from api.services.digest_service import get_digest_service

logger = structlog.get_logger()


@celery_app.task(bind=True, max_retries=2)
def send_test_digest(self, email: str, name: str = "Test User") -> Dict[str, Any]:
    """
    Send a test digest to a specific email address.

    Args:
        email: Email address to send to
        name: Name to use in email

    Returns:
        {
            "success": bool,
            "email": str,
            "article_count": int,
            "timestamp": str
        }
    """
    db = SessionLocal()

    try:
        logger.info(f"Generating test digest for {email}")

        # Build digest
        digest_builder = get_digest_builder(db)
        digest_data = digest_builder.build_test_digest(
            user_email=email,
            user_name=name
        )

        # Send email
        digest_service = get_digest_service()

        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        success = loop.run_until_complete(
            digest_service.send_digest(digest_data)
        )

        result = {
            "success": success,
            "email": email,
            "article_count": digest_data['article_count'],
            "timestamp": datetime.utcnow().isoformat(),
        }

        if success:
            logger.info(
                f"Test digest sent successfully to {email}",
                article_count=digest_data['article_count']
            )
        else:
            logger.error(f"Failed to send test digest to {email}")

        return result

    except Exception as exc:
        logger.error(f"Error sending test digest: {exc}", exc_info=True)
        raise self.retry(exc=exc)

    finally:
        db.close()


@celery_app.task(bind=True, max_retries=2, name="workers.tasks.digests.generate_user_digest")
def generate_user_digest(self, user_id: str) -> Dict[str, Any]:
    """
    Generate and send digest for a specific user.

    Args:
        user_id: User UUID

    Returns:
        {
            "success": bool,
            "user_id": str,
            "user_email": str,
            "article_count": int,
            "timestamp": str
        }
    """
    db = SessionLocal()

    try:
        logger.info(f"Generating digest for user {user_id}")

        # Get user
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise ValueError(f"User not found: {user_id}")

        if user.status != "active":
            logger.info(f"Skipping digest for inactive user {user_id}")
            return {
                "success": False,
                "user_id": user_id,
                "reason": "user_not_active",
                "timestamp": datetime.utcnow().isoformat(),
            }

        # Build digest
        digest_builder = get_digest_builder(db)
        digest_data = digest_builder.build_daily_digest(user)

        # Skip if no articles
        if digest_data['article_count'] == 0:
            logger.info(f"No articles for user {user_id}, skipping digest")
            return {
                "success": True,
                "user_id": user_id,
                "user_email": user.email,
                "article_count": 0,
                "skipped": True,
                "reason": "no_articles",
                "timestamp": datetime.utcnow().isoformat(),
            }

        # Send email
        digest_service = get_digest_service()

        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        success = loop.run_until_complete(
            digest_service.send_digest(digest_data)
        )

        result = {
            "success": success,
            "user_id": user_id,
            "user_email": user.email,
            "article_count": digest_data['article_count'],
            "personalized": digest_data['personalized'],
            "timestamp": datetime.utcnow().isoformat(),
        }

        if success:
            logger.info(
                f"Digest sent to {user.email}",
                article_count=digest_data['article_count'],
                personalized=digest_data['personalized']
            )
        else:
            logger.error(f"Failed to send digest to {user.email}")

        return result

    except Exception as exc:
        logger.error(f"Error generating digest for user {user_id}: {exc}", exc_info=True)
        raise self.retry(exc=exc)

    finally:
        db.close()


@celery_app.task(bind=True, name="workers.tasks.digests.generate_scheduled_digests")
def generate_scheduled_digests(self, hour: int = None) -> Dict[str, Any]:
    """
    Generate digests for all users scheduled for this hour.

    This task is called every hour by Celery Beat.
    It checks which users should receive their digest at this hour
    and queues individual digest generation tasks.

    Args:
        hour: Hour of day (0-23). If None, uses current UTC hour.

    Returns:
        {
            "success": bool,
            "hour": int,
            "users_found": int,
            "tasks_queued": int,
            "timestamp": str
        }
    """
    db = SessionLocal()

    try:
        if hour is None:
            hour = datetime.utcnow().hour

        logger.info(f"Generating scheduled digests for hour {hour}")

        # Find users scheduled for this hour
        # For MVP, we'll send to all active users
        # In production, you'd check UserPreference.digest_time
        users = (
            db.query(User)
            .filter(User.status == "active")
            .all()
        )

        logger.info(f"Found {len(users)} active users")

        # Queue individual digest tasks
        tasks_queued = []
        for user in users:
            task = generate_user_digest.delay(user.id)
            tasks_queued.append({
                "user_id": user.id,
                "user_email": user.email,
                "task_id": task.id
            })

        result = {
            "success": True,
            "hour": hour,
            "users_found": len(users),
            "tasks_queued": len(tasks_queued),
            "task_ids": [t["task_id"] for t in tasks_queued],
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info(
            f"Queued {len(tasks_queued)} digest generation tasks",
            hour=hour
        )

        return result

    except Exception as exc:
        logger.error(f"Error generating scheduled digests: {exc}", exc_info=True)
        raise

    finally:
        db.close()
