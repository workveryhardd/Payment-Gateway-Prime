from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "deposit_system",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "match-pending-deposits": {
            "task": "app.services.ledger_matcher.match_pending_deposits_task",
            "schedule": 60.0,  # Every 60 seconds
        },
        "flag-stale-deposits": {
            "task": "app.services.ledger_matcher.flag_stale_deposits_task",
            "schedule": 300.0,  # Every 5 minutes
        },
    },
)

