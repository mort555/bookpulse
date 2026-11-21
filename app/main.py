from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import redis
import structlog
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette.responses import JSONResponse, Response

# 1. Імпортуємо наш роутер авторизації
# ✅ Правильно
from app.api import api_router as auth_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.database.redis import close_redis, create_redis_client
from app.database.session import engine
from app.middlewares import setup_middlewares

configure_logging()

settings = get_settings()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    async_redis_client = create_redis_client()
    application.state.redis = async_redis_client
    redis_client = redis.Redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
    )

    logger.info("application_started")

    yield

    redis_client.close()
    await close_redis(async_redis_client)
    await engine.dispose()
    logger.info("application_stopped")


app = FastAPI(
    title="BookPulse",
    debug=settings.debug,
    lifespan=lifespan,
)

register_exception_handlers(app)
setup_middlewares(app)

# 2. Обов'язково підключаємо роутер до додатка!
app.include_router(auth_router)


@app.get("/health")
def health() -> Response:
    try:
        with engine.connect() as connection: # type: ignore
            connection.execute(text("SELECT 1")) # type: ignore

        redis_client = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        try:
            redis_client.ping()
        finally:
            redis_client.close()

    except (SQLAlchemyError, redis.RedisError, OSError):
        logger.warning("health_check_failed")
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable"},
        )

    return JSONResponse(
        status_code=200,
        content={"status": "ok"},
    )
