import redis.asyncio as redis
from polling.core.config import core

redis_client = redis.from_url(core.redis_url, decode_responses=True)
