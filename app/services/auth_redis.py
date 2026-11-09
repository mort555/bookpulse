import redis.asyncio as redis
from fastapi import HTTPException, status

# Підключення до Redis (можна винести URL у змінні середовища)
redis_client = redis.Redis.from_url("redis://localhost:6379/0", decode_responses=True)# type: ignore[assignment]

LOGIN_ATTEMPT_LIMIT = 5
LOGIN_WINDOW_SECONDS = 900  # 15 хвилин


async def check_login_rate_limit(identifier: str) -> None:
    """Перевірка кількості невдалих спроб входу (ліміт: 5 за 15 хв)."""
    key = f"login_attempts:{identifier}"
    attempts = await redis_client.get(key)

    if attempts and int(attempts) >= LOGIN_ATTEMPT_LIMIT:
        ttl = await redis_client.ttl(key)
        retry_after = ttl if ttl > 0 else LOGIN_WINDOW_SECONDS
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )


async def increment_login_attempts(identifier: str) -> None:
    """Збільшення лічильника невдалих спроб входу."""
    key = f"login_attempts:{identifier}"
    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, LOGIN_WINDOW_SECONDS)
    await pipe.execute()


async def clear_login_attempts(identifier: str) -> None:
    """Очищення спроб після успішного входу."""
    key = f"login_attempts:{identifier}"
    await redis_client.delete(key)


async def store_refresh_token(
    user_id: int, token_jti: str, expire_seconds: int
) -> None:
    """Зберігання активного refresh-токена в Redis."""
    key = f"refresh_token:{user_id}:{token_jti}"
    await redis_client.setex(key, expire_seconds, "active")


async def revoke_refresh_token(user_id: int, token_jti: str) -> None:
    """Анулювання (ротація/логаут) refresh-токена."""
    key = f"refresh_token:{user_id}:{token_jti}"
    await redis_client.delete(key)


async def is_refresh_token_valid(user_id: int, token_jti: str) -> bool:
    """Перевірка чи активний токен у Redis."""
    key = f"refresh_token:{user_id}:{token_jti}"
    val = await redis_client.get(key)
    return val == "active"
