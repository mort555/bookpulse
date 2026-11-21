from __future__ import annotations

from typing import cast

from fastapi import Request
from redis.asyncio import Redis

from app.core.config import get_settings


def create_redis_client() -> Redis[str]:
    return Redis.from_url(
        get_settings().redis_url,
        decode_responses=True,
    )


async def get_redis(request: Request) -> Redis[str]:
    return cast(Redis[str], request.app.state.redis)


async def close_redis(redis_client: Redis[str]) -> None:
    await redis_client.aclose()  # type: ignore[attr-defined]
