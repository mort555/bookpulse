from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: list[dict[str, Any]] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or [],
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return error_response(
            status_code=422,
            code="VALIDATION_ERROR",
            message="Request validation failed.",
            details=[
                {
                    "location": list(error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
                for error in exc.errors()
            ],
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        error_map = {
            401: ("UNAUTHORIZED", "Authentication required."),
            403: ("FORBIDDEN", "Access forbidden."),
            404: ("NOT_FOUND", "Resource not found."),
            409: ("CONFLICT", "Resource conflict."),
            429: ("RATE_LIMITED", "Too many requests."),
        }

        code, message = error_map.get(
            exc.status_code,
            ("HTTP_ERROR", str(exc.detail)),
        )

        return error_response(
            status_code=exc.status_code,
            code=code,
            message=message,
        )
