import logging
import os
import time
from datetime import datetime, timedelta, timezone

from redis import Redis
from rq import Queue


DEFAULT_REDIS_URL = "redis://localhost:6379/0"


def get_redis_url():
    try:
        from flask import current_app

        return current_app.config.get("REDIS_URL", DEFAULT_REDIS_URL)
    except Exception:
        return os.getenv("REDIS_URL", DEFAULT_REDIS_URL)


def get_redis_connection():
    return Redis.from_url(get_redis_url())


def get_queue():
    return Queue("default", connection=get_redis_connection())


def to_utc(value):
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def should_queue_notification(due_date, now=None):
    if not due_date:
        return False

    due_utc = to_utc(due_date)
    now_utc = to_utc(now or datetime.now(timezone.utc))

    if due_utc <= now_utc:
        return False

    return due_utc <= now_utc + timedelta(hours=24)


def send_due_date_notification(task_title):
    time.sleep(5)
    logging.getLogger(__name__).info(
        "Reminder: Task '%s' is due soon!", task_title
    )
