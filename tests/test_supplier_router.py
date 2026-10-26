from unittest.mock import MagicMock

from app.api.dependencies import get_supplier_service
from app.infra.database.models import Supplier
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def create_supplier() -> Supplier:
    return Supplier(
        id=1,
        name="Test Supplier",
        website_url="https://example.com",
        is_active=True,
    )


def test_list_suppliers_returns_200() -> None:
    mock_service = MagicMock()
    mock_service.list_suppliers.return_value = [create_supplier()]

    app.dependency_overrides[get_supplier_service] = lambda: mock_service

    try:
        response = client.get("/api/v1/suppliers")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Test Supplier"


def test_get_supplier_returns_200() -> None:
    mock_service = MagicMock()
    mock_service.get_supplier.return_value = create_supplier()

    app.dependency_overrides[get_supplier_service] = lambda: mock_service

    try:
        response = client.get("/api/v1/suppliers/1")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["website_url"] == "https://example.com"


def test_get_missing_supplier_returns_404() -> None:
    mock_service = MagicMock()
    mock_service.get_supplier.return_value = None

    app.dependency_overrides[get_supplier_service] = lambda: mock_service

    try:
        response = client.get("/api/v1/suppliers/999")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "NOT_FOUND",
            "message": "Supplier not found.",
            "details": [],
        }
    }


def test_create_supplier_returns_201() -> None:
    mock_service = MagicMock()
    mock_service.create_supplier.return_value = create_supplier()

    app.dependency_overrides[get_supplier_service] = lambda: mock_service

    try:
        response = client.post(
            "/api/v1/suppliers",
            json={
                "name": "Test Supplier",
                "website_url": "https://example.com",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["name"] == "Test Supplier"

    mock_service.create_supplier.assert_called_once_with(
        name="Test Supplier",
        website_url="https://example.com/",
    )


def test_create_supplier_rejects_invalid_url() -> None:
    response = client.post(
        "/api/v1/suppliers",
        json={
            "name": "Test Supplier",
            "website_url": "not-a-url",
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
