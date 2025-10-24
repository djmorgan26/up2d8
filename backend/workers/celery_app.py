"""Celery application configuration for UP2D8.

Handles background tasks for:
- Content scraping
- Article processing
- Digest generation
- Email delivery
"""

import os
from celery import Celery
from celery.schedules import crontab

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Create Celery app
celery_app = Celery(
    "up2d8",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "workers.tasks.scraping",
        "workers.tasks.processing",
        "workers.tasks.digests",
    ],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Task execution
    task_track_started=True,
    task_time_limit=300,  # 5 minutes hard limit
    task_soft_time_limit=240,  # 4 minutes soft limit

    # Result backend
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={
        "master_name": "mymaster",
    },

    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,

    # Rate limiting
    task_default_rate_limit="100/m",  # 100 tasks per minute

    # Retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,

    # Logging
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s",
)

# Beat schedule (periodic tasks)
celery_app.conf.beat_schedule = {
    # High priority sources - every 2 hours
    "scrape-high-priority-sources": {
        "task": "workers.tasks.scraping.scrape_priority_sources",
        "schedule": crontab(minute=0, hour="*/2"),  # Every 2 hours
        "args": ("high",),
    },

    # Medium priority sources - every 6 hours
    "scrape-medium-priority-sources": {
        "task": "workers.tasks.scraping.scrape_priority_sources",
        "schedule": crontab(minute=0, hour="*/6"),  # Every 6 hours
        "args": ("medium",),
    },

    # Low priority sources - daily at 2 AM
    "scrape-low-priority-sources": {
        "task": "workers.tasks.scraping.scrape_priority_sources",
        "schedule": crontab(minute=0, hour=2),  # Daily at 2 AM
        "args": ("low",),
    },

    # Process pending articles - every 15 minutes
    "process-pending-articles": {
        "task": "workers.tasks.processing.process_pending_articles",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
    },

    # Generate daily digests - every hour (checks which users need digests)
    "generate-daily-digests": {
        "task": "workers.tasks.digests.generate_scheduled_digests",
        "schedule": crontab(minute=0),  # Every hour on the hour
    },

    # Cleanup old data - daily at 3 AM
    "cleanup-old-data": {
        "task": "workers.tasks.maintenance.cleanup_old_data",
        "schedule": crontab(minute=0, hour=3),  # Daily at 3 AM
    },
}

# Task routes (for queue prioritization) - disabled for MVP, all tasks use default queue
# celery_app.conf.task_routes = {
#     "workers.tasks.scraping.*": {"queue": "scraping"},
#     "workers.tasks.processing.*": {"queue": "processing"},
#     "workers.tasks.digests.*": {"queue": "digests"},
#     "workers.tasks.maintenance.*": {"queue": "maintenance"},
# }

# Task priorities
celery_app.conf.task_default_priority = 5
celery_app.conf.task_queue_max_priority = 10


if __name__ == "__main__":
    celery_app.start()
