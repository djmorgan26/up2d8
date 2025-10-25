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

        # Create Digest record in database for tracking
        from api.db.models import Digest
        import uuid as uuid_lib

        digest_record = Digest(
            id=str(uuid_lib.uuid4()),
            user_id=user.id,
            digest_date=datetime.utcnow().date(),
            scheduled_for=datetime.utcnow(),
            article_count=digest_data['article_count'],
            personalized_intro=None,
            delivery_status="pending",
        )
        db.add(digest_record)
        db.commit()
        db.refresh(digest_record)

        # Add digest_id to digest_data for email template
        digest_data['digest_id'] = digest_record.id

        # Send email
        digest_service = get_digest_service()

        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        success = loop.run_until_complete(
            digest_service.send_digest(digest_data)
        )

        # Update digest record based on success
        if success:
            digest_record.delivery_status = "sent"
            digest_record.sent_at = datetime.utcnow()
        else:
            digest_record.delivery_status = "failed"
            digest_record.delivery_error = "Email sending failed"

        db.commit()

        result = {
            "success": success,
            "user_id": user_id,
            "user_email": user.email,
            "article_count": digest_data['article_count'],
            "personalized": digest_data['personalized'],
            "digest_id": digest_record.id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if success:
            logger.info(
                f"Digest sent to {user.email}",
                article_count=digest_data['article_count'],
                personalized=digest_data['personalized'],
                digest_id=digest_record.id
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

    The task uses timezone-aware logic:
    1. Get current UTC hour
    2. For each active user with preferences:
       - Convert their local delivery time to UTC
       - If it matches current UTC hour, queue digest

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
    from datetime import timezone as dt_timezone
    import pytz

    db = SessionLocal()

    try:
        if hour is None:
            hour = datetime.utcnow().hour

        logger.info(f"Generating scheduled digests for UTC hour {hour}")

        # Find users who should receive digest at this hour
        # Get all active users with preferences
        users_with_prefs = (
            db.query(User, UserPreference)
            .join(UserPreference, User.id == UserPreference.user_id)
            .filter(User.status == "active")
            .filter(UserPreference.digest_frequency == "daily")
            .all()
        )

        logger.info(f"Found {len(users_with_prefs)} active users with daily digest preference")

        # Queue individual digest tasks for users scheduled at this hour
        tasks_queued = []
        for user, preferences in users_with_prefs:
            try:
                # Get user's timezone and delivery time
                user_tz = pytz.timezone(preferences.timezone)
                delivery_time = preferences.delivery_time

                # Get current time in user's timezone
                current_utc = datetime.utcnow().replace(tzinfo=pytz.UTC)
                current_user_time = current_utc.astimezone(user_tz)

                # Check if current hour matches delivery hour in user's timezone
                if current_user_time.hour == delivery_time.hour:
                    # Check if today is in delivery_days (1=Mon, 7=Sun)
                    weekday = current_user_time.isoweekday()
                    if weekday in preferences.delivery_days:
                        task = generate_user_digest.delay(user.id)
                        tasks_queued.append({
                            "user_id": user.id,
                            "user_email": user.email,
                            "user_timezone": preferences.timezone,
                            "user_local_time": current_user_time.strftime("%H:%M"),
                            "task_id": task.id
                        })
                        logger.info(
                            f"Queued digest for {user.email}",
                            user_timezone=preferences.timezone,
                            user_local_time=current_user_time.strftime("%H:%M"),
                            weekday=weekday
                        )
            except Exception as user_error:
                logger.error(
                    f"Error processing user {user.email}: {user_error}",
                    exc_info=True
                )
                continue

        result = {
            "success": True,
            "utc_hour": hour,
            "users_checked": len(users_with_prefs),
            "tasks_queued": len(tasks_queued),
            "task_ids": [t["task_id"] for t in tasks_queued],
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info(
            f"Queued {len(tasks_queued)} digest generation tasks for UTC hour {hour}",
            users_checked=len(users_with_prefs)
        )

        return result

    except Exception as exc:
        logger.error(f"Error generating scheduled digests: {exc}", exc_info=True)
        raise

    finally:
        db.close()
