"""
Redis client wrapper for TradeFlow.

Per SAD Section 11: Redis is used for cache, sessions, tokens, rate limiting.
This provides a centralized client initialization point.
"""

import logging

from django.conf import settings
from django.core.cache import caches

logger = logging.getLogger(__name__)


def get_redis_client():
    """
    Return the default Django Redis cache client.

    Usage:
        client = get_redis_client()
        client.get("key")
        client.set("key", "value", timeout=300)
    """
    return caches["default"]


def get_celery_queue_client():
    """
    Return a Redis client configured for Celery broker operations.

    Used for job queue management, monitoring, and priority routing.
    """
    from django_redis import get_redis_connection
    return get_redis_connection("celery")