from unittest.mock import MagicMock

import pytest
from app.core.exceptions import ConflictError
from app.services.supplier_service import SupplierService


@pytest.fixture
def setup_service() -> tuple[SupplierService, MagicMock, MagicMock]:
    session = MagicMock()
    session_factory = MagicMock(return_value=session)
    service = SupplierService(session_factory)

    return service, session, session_factory


def test_get_supplier(setup_service: tuple) -> None:
    service, session, _ = setup_service
    supplier = MagicMock()
    session.scalar.return_value = supplier

    result = service.get_supplier(1)

    assert result is supplier
    session.commit.assert_called_once()
    session.close.assert_called_once()


def test_list_suppliers(setup_service: tuple) -> None:
    service, session, _ = setup_service
    suppliers = [MagicMock(), MagicMock()]
    session.scalars.return_value.all.return_value = suppliers

    result = service.list_suppliers()

    assert result == suppliers
    session.commit.assert_called_once()


def test_list_active_suppliers(setup_service: tuple) -> None:
    service, session, _ = setup_service

    service.list_suppliers(active_only=True)

    session.scalars.assert_called_once()
    session.commit.assert_called_once()


def test_create_supplier(setup_service: tuple) -> None:
    service, session, _ = setup_service
    session.scalar.return_value = None
    session.flush.return_value = None

    result = service.create_supplier(
        name="Test Supplier",
        website_url="https://example.com",
    )

    assert result.name == "Test Supplier"
    assert result.website_url == "https://example.com"
    session.commit.assert_called_once()


def test_create_duplicate_supplier(setup_service: tuple) -> None:
    service, session, _ = setup_service
    session.scalar.return_value = MagicMock()

    with pytest.raises(
        ConflictError,
        match="Supplier with this name already exists.",
    ):
        service.create_supplier(
            name="Existing Supplier",
            website_url="https://example.com",
        )

    session.rollback.assert_called_once()
    session.close.assert_called_once()
