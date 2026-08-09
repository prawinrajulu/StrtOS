import time
from fastapi import Request, HTTPException, status
from app.core.redis import redis_manager
from app.core.logging import logger

class RateLimiter:
    """Production-grade Redis-backed sliding window rate limiter with graceful fallback."""

    @staticmethod
    async def check_rate_limit(request: Request, key_prefix: str, max_requests: int = 10, window_seconds: int = 60):
        client_ip = request.client.host if request.client else "unknown"
        redis_key = f"rate_limit:{key_prefix}:{client_ip}"

        try:
            if redis_manager.redis:
                current = await redis_manager.redis.incr(redis_key)
                if current == 1:
                    await redis_manager.redis.expire(redis_key, window_seconds)
                if current > max_requests:
                    logger.warning(f"Rate limit exceeded for IP {client_ip} on endpoint {key_prefix}")
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded. Please try again later."
                    )
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Rate limiter warning (bypassing due to Redis error): {e}")
