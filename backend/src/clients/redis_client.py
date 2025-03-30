from redis.asyncio import Redis

from src.config import settings

redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)


async def get_redis_client() -> Redis:
    return redis
