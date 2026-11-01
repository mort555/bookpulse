from unittest.mock import MagicMock, patch

import redis
from app.main import app
from fastapi.testclient import TestClient


def test_health_returns_ok() -> None:
    redis_client = MagicMock()
    redis_client.ping.return_value = True

    with (
        patch("app.main.engine.connect") as mock_connect,
        patch("app.main.redis.Redis.from_url", return_value=redis_client),
    ):
        mock_connect.return_value.__enter__.return_value.execute.return_value = None

        with TestClient(app) as client:
            response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "X-Request-ID" in response.headers


def test_health_returns_503_when_redis_is_unavailable() -> None:
    redis_client = MagicMock()
    redis_client.ping.side_effect = redis.RedisError("Redis unavailable")

    with (
        patch("app.main.engine.connect") as mock_connect,
        patch("app.main.redis.Redis.from_url", return_value=redis_client),
    ):
        mock_connect.return_value.__enter__.return_value.execute.return_value = None

        with TestClient(app) as client:
            response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}


def test_unknown_url_returns_standard_error() -> None:
    with TestClient(app) as client:
        response = client.get("/unknown-url")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "label": "NOT_FOUND",
            "message": "Resource not found.",
        }
    }
