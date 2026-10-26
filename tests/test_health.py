from unittest.mock import patch

import redis
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_returns_ok() -> None:
    with (
        patch("app.main.engine.connect") as mock_db,
        patch("app.main.redis_client.ping", return_value=True),
    ):
        mock_db.return_value.__enter__.return_value.execute.return_value = None

        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "db": "ok",
        "redis": "ok",
    }


def test_unknown_route_returns_standard_error() -> None:
    response = client.get("/not-existing")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "NOT_FOUND",
            "message": "Resource not found.",
            "details": [],
        }
    }


def test_health_returns_503_when_redis_is_unavailable() -> None:
    with (
        patch("app.main.engine.connect") as mock_db,
        patch("app.main.redis_client.ping", side_effect=redis.RedisError),
    ):
        mock_db.return_value.__enter__.return_value.execute.return_value = None

        response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {
        "status": "error",
        "db": "ok",
        "redis": "error",
    }
