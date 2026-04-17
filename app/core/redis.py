import redis

from app.core.config import get_settings


def get_redis() -> redis.Redis:
    """Return a Redis client instance."""
    return redis.from_url(get_settings().redis_url, decode_responses=True)