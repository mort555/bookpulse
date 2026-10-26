from unittest.mock import MagicMock

from app.infra.database.models import Supplier
from app.repositories.supplier_repository import SupplierRepository


def test_get_by_id_returns_supplier() -> None:
    session = MagicMock()
    supplier = Supplier(
        id=1,
        name="Book Store",
        website_url="https://example.com",
        is_active=True,
    )
    session.scalar.return_value = supplier

    repository = SupplierRepository(session)

    result = repository.get_by_id(1)

    assert result is supplier
    session.scalar.assert_called_once()


def test_get_by_name_returns_supplier() -> None:
    session = MagicMock()
    supplier = Supplier(
        id=1,
        name="Book Store",
        website_url="https://example.com",
        is_active=True,
    )
    session.scalar.return_value = supplier

    repository = SupplierRepository(session)

    result = repository.get_by_name("Book Store")

    assert result is supplier
    session.scalar.assert_called_once()


def test_list_all_returns_suppliers() -> None:
    session = MagicMock()
    suppliers = [
        Supplier(
            id=1,
            name="Book Store",
            website_url="https://example.com",
            is_active=True,
        )
    ]
    session.scalars.return_value.all.return_value = suppliers

    repository = SupplierRepository(session)

    result = repository.list_all()

    assert result == suppliers
    session.scalars.assert_called_once()


def test_list_all_can_filter_active_suppliers() -> None:
    session = MagicMock()
    session.scalars.return_value.all.return_value = []

    repository = SupplierRepository(session)

    result = repository.list_all(active_only=True)

    assert result == []
    session.scalars.assert_called_once()


def test_create_adds_and_flushes_supplier() -> None:
    session = MagicMock()
    session.flush.side_effect = lambda: None

    repository = SupplierRepository(session)

    result = repository.create(
        name="Book Store",
        website_url="https://example.com",
    )

    assert result.name == "Book Store"
    assert result.website_url == "https://example.com"
    assert result.is_active is True
    session.add.assert_called_once_with(result)
    session.flush.assert_called_once()
