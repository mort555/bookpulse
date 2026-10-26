from app.core.exceptions import (
    AppException,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    RateLimitedError,
    UnauthorizedError,
    register_exception_handlers,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient


def create_test_app() -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/conflict")
    def conflict() -> None:
        raise ConflictError("Supplier already exists.")

    @app.get("/not-found")
    def not_found() -> None:
        raise NotFoundError("Supplier not found.")

    @app.get("/unauthorized")
    def unauthorized() -> None:
        raise UnauthorizedError()

    @app.get("/forbidden")
    def forbidden() -> None:
        raise ForbiddenError()

    @app.get("/rate-limited")
    def rate_limited() -> None:
        raise RateLimitedError()

    @app.get("/custom-error")
    def custom_error() -> None:
        raise AppException(
            "Unexpected application error.",
            status_code=500,
            code="INTERNAL_ERROR",
        )

    return app


def test_conflict_error_response() -> None:
    client = TestClient(create_test_app())

    response = client.get("/conflict")

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"
    assert response.json()["error"]["message"] == "Supplier already exists."


def test_not_found_error_response() -> None:
    client = TestClient(create_test_app())

    response = client.get("/not-found")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_unauthorized_error_response() -> None:
    client = TestClient(create_test_app())

    response = client.get("/unauthorized")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_forbidden_error_response() -> None:
    client = TestClient(create_test_app())

    response = client.get("/forbidden")

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_rate_limited_error_response() -> None:
    client = TestClient(create_test_app())

    response = client.get("/rate-limited")

    assert response.status_code == 429
    assert response.json()["error"]["code"] == "RATE_LIMITED"


def test_custom_app_exception_response() -> None:
    client = TestClient(create_test_app())

    response = client.get("/custom-error")

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "INTERNAL_ERROR"
    assert response.json()["error"]["details"] == []
