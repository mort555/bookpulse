from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import redis
import structlog
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette.responses import JSONResponse, Response

from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.database.session import engine
from app.middlewares.request_id import RequestIDMiddleware

configure_logging()

settings = get_settings()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    redis_client = redis.Redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
    )

    logger.info("application_started")

    yield

    redis_client.close()
    engine.dispose()
    logger.info("application_stopped")


app = FastAPI(
    title="BookPulse",
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(RequestIDMiddleware)
register_exception_handlers(app)


@app.get("/health")
def health() -> Response:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

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
