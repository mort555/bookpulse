from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from uuid import uuid4

import redis
import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from starlette.responses import Response
from structlog.contextvars import bind_contextvars, clear_contextvars

from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging

configure_logging()

settings = get_settings()
logger = structlog.get_logger()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

redis_client = redis.Redis.from_url(
    settings.redis_url,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("application_started", app_name=settings.app_name)
    yield
    redis_client.close()
    engine.dispose()
    logger.info("application_stopped", app_name=settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

register_exception_handlers(app)


@app.middleware("http")
async def add_request_id(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    request_id = request.headers.get("X-Request-ID")

    if not request_id:
        request_id = str(uuid4())

    request.state.request_id = request_id
    clear_contextvars()
    bind_contextvars(request_id=request_id)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response


@app.exception_handler(Exception)
async def internal_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")

    logger.error(
        "unhandled_exception",
        request_id=request_id,
        error=str(exc),
        path=request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
                "details": [],
            }
        },
    )


@app.get("/health", tags=["Health"])
def health_check() -> JSONResponse:
    status: dict[str, str] = {
        "status": "ok",
        "db": "ok",
        "redis": "ok",
    }

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        status["db"] = "error"

    try:
        redis_client.ping()
    except redis.RedisError:
        status["redis"] = "error"

    if status["db"] != "ok" or status["redis"] != "ok":
        status["status"] = "error"
        return JSONResponse(status_code=503, content=status)

    return JSONResponse(status_code=200, content=status)


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"message": "BookPulse API"}
