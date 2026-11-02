# app/core/exceptions.py

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = structlog.get_logger()


class AppException(Exception):
    """Базовий клас для всіх кастомних винятків застосунку."""

    def __init__(
        self,
        label: str = "BAD_REQUEST",
        status_code: int = 400,
        detail: str | None = None,
    ):
        self.label = label
        self.status_code = status_code
        self.detail = detail
        super().__init__(label)


class NotFoundError(AppException):
    def __init__(self, detail: str | None = None):
        super().__init__(label="NOT_FOUND", status_code=404, detail=detail)


class ConflictError(AppException):
    def __init__(self, detail: str | None = None):
        super().__init__(label="CONFLICT", status_code=409, detail=detail)


class ForbiddenError(AppException):
    def __init__(self, detail: str | None = None):
        super().__init__(label="FORBIDDEN", status_code=403, detail=detail)


class BadRequestError(AppException):
    def __init__(self, detail: str | None = None):
        super().__init__(label="BAD_REQUEST", status_code=400, detail=detail)


# Реєстрація обробників (Exception Handlers)
def register_exception_handlers(app: FastAPI) -> None:

    # Єдиний хендлер для всіх кастомних бізнес-помилок завдяки поліморфізму
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        await logger.awarn(
            "app_exception",
            label=exc.label,
            status_code=exc.status_code,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.label,
                    "message": exc.detail or "An error occurred",
                }
            },
        )

    # Обробка валідації Pydantic (422)
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        await logger.awarn(
            "validation_error", path=request.url.path, errors=exc.errors()
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": f"Invalid request parameters: {exc.errors()}",
                }
            },
        )

    # Стандартні HTTP-помилки Starlette (наприклад, 404 роутера, 405 Method Not Allowed)
    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "HTTP_EXCEPTION",
                    "message": exc.detail,
                }
            },
        )

    # Непередбачувані помилки сервера (500 Internal Server Error)
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
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
