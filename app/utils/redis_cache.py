import json
import logging

from redis.asyncio import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


async def get_cached_json(redis: Redis | None, key: str):
    """None means cache miss/unavailable; the service must query the database."""
    if redis is None:
        return None
    try:
        value = await redis.get(key)
        return json.loads(value) if value is not None else None
    except (RedisError, OSError, ValueError):
        logger.warning("Cache read failed; use database fallback")
        return None


async def set_cached_json(redis: Redis | None, key: str, value, ttl: int) -> bool:
    if redis is None:
        return False
    try:
        await redis.set(key, json.dumps(value, ensure_ascii=False), ex=ttl)
        return True
    except (RedisError, OSError):
        logger.warning("Cache write failed; continuing without cache")
        return False
