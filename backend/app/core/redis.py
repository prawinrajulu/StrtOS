import asyncio
from typing import Optional, AsyncGenerator
import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logging import logger

class RedisManager:
    """
    Enterprise Redis Connection & Event Pub/Sub Manager.
    Supports Connection Pooling, Health Check, Pub/Sub Publishing and Subscribing.
    """
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self.pubsub: Optional[aioredis.client.PubSub] = None

    async def connect(self):
        try:
            self.redis = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis.ping()
            logger.info("Successfully connected to Redis.")
        except Exception as e:
            logger.warning(f"Redis connection warning (running fallback mode): {e}")

    async def disconnect(self):
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis.")

    async def check_health(self) -> bool:
        if not self.redis:
            return False
        try:
            return await self.redis.ping()
        except Exception:
            return False

    async def publish_event(self, channel: str, message: str):
        if self.redis:
            try:
                await self.redis.publish(channel, message)
            except Exception as e:
                logger.error(f"Error publishing to Redis channel {channel}: {e}")

    async def subscribe_channel(self, channel: str) -> AsyncGenerator[str, None]:
        if self.redis:
            pubsub = self.redis.pubsub()
            await pubsub.subscribe(channel)
            try:
                async for msg in pubsub.listen():
                    if msg["type"] == "message":
                        yield msg["data"]
            finally:
                await pubsub.unsubscribe(channel)

redis_manager = RedisManager()
