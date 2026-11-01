import json
from collections.abc import Mapping, Sequence
from http import HTTPStatus
from typing import Any

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = structlog.get_logger(__name__)

ERROR_MAP: dict[int, tuple[str, str]] = {
    400: ("BAD_REQUEST", "Malformed request."),
    401: ("UNAUTHORIZED", "Authentication required."),
    403: ("FORBIDDEN", "Access forbidden."),
    404: ("NOT_FOUND", "Resource not found."),
    405: ("METHOD_NOT_ALLOWED", "Method not allowed for this resource."),
    409: ("CONFLICT", "Resource conflict."),
    410: ("GONE", "Resource no longer available."),
    415: ("UNSUPPORTED_MEDIA_TYPE", "Unsupported media type."),
    422: ("UNPROCESSABLE_ENTITY", "Request could not be processed."),
    429: ("RATE_LIMITED", "Too many requests."),
    500: ("INTERNAL_ERROR", "An unexpected error occurred."),
    502: ("BAD_GATEWAY", "Upstream service returned an invalid response."),
    503: ("SERVICE_UNAVAILABLE", "Service temporarily unavailable."),
    504: ("GATEWAY_TIMEOUT", "Upstream service timed out."),
}

FALLBACK_LABEL = "HTTP_ERROR"
FALLBACK_MESSAGE = "Request failed."
VALIDATION_LABEL = "VALIDATION_ERROR"


class AppException(Exception):
    """Base class for errors rendered as a structured JSON response."""

    status_code: int = 500
    label: str = "INTERNAL_ERROR"
    default_message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        *,
        status_code: int | None = None,
        label: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        resolved_status = status_code if status_code is not None else self.status_code
        resolved_label = label if label is not None else self.label
        resolved_message = message if message is not None else self.default_message

        self.status_code = resolved_status
        self.label = resolved_label
        self.message = resolved_message
        self.headers = headers

        super().__init__(resolved_message)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(status_code={self.status_code!r}, "
            f"label={self.label!r}, message={self.message!r})"
        )


class NotFoundError(AppException):
    status_code = 404
    label = "NOT_FOUND"
    default_message = "Resource not found."


class ConflictError(AppException):
    status_code = 409
    label = "CONFLICT"
    default_message = "Resource conflict."


class UnauthorizedError(AppException):
    status_code = 401
    label = "UNAUTHORIZED"
    default_message = "Authentication required."


class ForbiddenError(AppException):
    status_code = 403
    label = "FORBIDDEN"
    default_message = "Access forbidden."


class RateLimitedError(AppException):
    status_code = 429
    label = "RATE_LIMITED"
    default_message = "Too many requests."


def error_response(
    status_code: int,
    label: str,
    message: str,
    *,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"label": label, "message": message}},
        headers=headers,
    )


def status_phrase(status_code: int) -> str:
    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return ""


def format_validation_errors(errors: Sequence[Mapping[str, Any]]) -> str:
    return "; ".join(
        f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
        for error in errors
    )


def request_context(request: Request) -> dict[str, Any]:
    return {
        "path": request.url.path,
        "request_id": getattr(request.state, "request_id", None),
    }


def is_server_error(status_code: int) -> bool:
    return status_code >= 500


def log_failed_request(
    request: Request,
    event: str,
    *,
    status_code: int,
    label: str,
    error: str,
    exc: BaseException | None = None,
) -> None:
    """A failure while logging must never break the error response itself."""
    try:
        logger.error(
            event,
            status_code=status_code,
            label=label,
            error=error,
            exc_info=exc if exc is not None else False,
            **request_context(request),
        )
    except Exception:
        return


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException,
    ) -> JSONResponse:
        if is_server_error(exc.status_code):
            log_failed_request(
                request,
                "request_failed",
                status_code=exc.status_code,
                label=exc.label,
                error=exc.message,
            )

        return error_response(
            status_code=exc.status_code,
            label=exc.label,
            message=exc.message,
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        message = "Request validation failed."
        details = format_validation_errors(exc.errors())
        if details:
            message = f"{message} Details: {details}."

        return error_response(
            status_code=422,
            label=VALIDATION_LABEL,
            message=message,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        label, message = ERROR_MAP.get(
            exc.status_code,
            (FALLBACK_LABEL, ""),
        )
        if not message:
            message = status_phrase(exc.status_code) or FALLBACK_MESSAGE

        phrase = status_phrase(exc.status_code)
        detail = exc.detail
        if isinstance(detail, str) and detail:
            if detail != phrase:
                message = detail
        elif detail is not None:
            message = json.dumps(detail, ensure_ascii=False, default=str)

        if is_server_error(exc.status_code):
            log_failed_request(
                request,
                "request_failed",
                status_code=exc.status_code,
                label=label,
                error=message,
            )

        return error_response(
            status_code=exc.status_code,
            label=label,
            message=message,
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        log_failed_request(
            request,
            "unhandled_exception",
            status_code=500,
            label="INTERNAL_ERROR",
            error=repr(exc),
            exc=exc,
        )

        return error_response(
            status_code=500,
            label="INTERNAL_ERROR",
            message="An unexpected error occurred.",
        )
