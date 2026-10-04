from typing import Optional
import redis.asyncio as aioredis
from app.core.config import settings

redis_client: Optional[aioredis.Redis] = None


async def get_redis_client() -> aioredis.Redis:
    """Синглтон асинхронного клиента Redis."""
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return redis_client


async def close_redis() -> None:
    """Корректное закрытие соединений при остановке сервиса."""
    global redis_client
    if redis_client is not None:
        await redis_client.aclose()
        redis_client = None