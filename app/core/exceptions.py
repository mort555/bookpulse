import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError
from redis.exceptions import TimeoutError as RedisTimeoutError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = structlog.get_logger()


class AppException(Exception):
    """Base class for application exceptions."""

    default_label = "BAD_REQUEST"
    default_status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "An error occurred"

    def __init__(
        self,
        label: str | None = None,
        status_code: int | None = None,
        detail: str | None = None,
    ) -> None:
        self.label = label or self.default_label
        self.status_code = (
            status_code if status_code is not None else self.default_status_code
        )
        self.detail = detail or self.default_detail
        super().__init__(self.detail)


class DomainError(AppException):
    """A business rule or entity state violation."""

    default_label = "DOMAIN_ERROR"
    default_status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    default_detail = "A business rule was violated"

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail=detail)


class NotFoundError(DomainError):
    default_label = "NOT_FOUND"
    default_status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resource not found"


class ConflictError(DomainError):
    default_label = "CONFLICT"
    default_status_code = status.HTTP_409_CONFLICT
    default_detail = "Resource state conflict"


class PermissionDeniedError(DomainError):
    default_label = "FORBIDDEN"
    default_status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Permission denied"


class ForbiddenError(PermissionDeniedError):
    """Backward-compatible name for permission errors."""


class BadRequestError(DomainError):
    default_label = "BAD_REQUEST"
    default_status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid request"


class DatabaseError(AppException):
    """A database or data integrity failure."""

    default_label = "DATABASE_ERROR"
    default_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "A database error occurred"

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail=detail)


class DuplicateRecordError(DatabaseError, ConflictError):
    """A database uniqueness conflict."""

    default_label = "DUPLICATE_RECORD"
    default_status_code = status.HTTP_409_CONFLICT
    default_detail = "Record already exists"

    def __init__(self, detail: str | None = None) -> None:
        AppException.__init__(self, detail=detail)


class ServiceError(AppException):
    """An integration, queue, cache, or external service failure."""

    default_label = "SERVICE_ERROR"
    default_status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = "An external service error occurred"

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail=detail)


class ExternalTimeoutError(ServiceError):
    default_label = "EXTERNAL_TIMEOUT"
    default_status_code = status.HTTP_504_GATEWAY_TIMEOUT
    default_detail = "The external service timed out"


def _app_error_response(exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.label,
                "message": exc.detail,
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        await logger.awarn(
            "app_exception",
            label=exc.label,
            status_code=exc.status_code,
            path=request.url.path,
            exception_type=type(exc).__name__,
        )
        return _app_error_response(exc)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        await logger.awarn(
            "validation_error", path=request.url.path, errors=exc.errors()
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": f"Invalid request parameters: {exc.errors()}",
                }
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        await logger.awarn(
            "http_exception",
            path=request.url.path,
            status_code=exc.status_code,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "HTTP_EXCEPTION",
                    "message": exc.detail,
                }
            },
            headers=exc.headers,
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        await logger.aerror(
            "database_error",
            path=request.url.path,
            method=request.method,
            exception_type=type(exc).__name__,
            error=str(exc),
        )
        return _app_error_response(DatabaseError())

    @app.exception_handler(RedisTimeoutError)
    async def redis_timeout_exception_handler(
        request: Request, exc: RedisTimeoutError
    ) -> JSONResponse:
        await logger.aerror(
            "external_service_timeout",
            path=request.url.path,
            method=request.method,
            exception_type=type(exc).__name__,
            error=str(exc),
        )
        return _app_error_response(ExternalTimeoutError())

    @app.exception_handler(RedisError)
    async def redis_exception_handler(
        request: Request, exc: RedisError
    ) -> JSONResponse:
        await logger.aerror(
            "external_service_error",
            path=request.url.path,
            method=request.method,
            exception_type=type(exc).__name__,
            error=str(exc),
        )
        return _app_error_response(ServiceError())

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        await logger.aexception(
            "unhandled_exception",
            path=request.url.path,
            method=request.method,
            error=str(exc),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An internal server error occurred",
                }
            },
        )
