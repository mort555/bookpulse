from collections.abc import Callable

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError
from app.infra.database.models import Supplier
from app.infra.database.unit_of_work import SqlAlchemyUnitOfWork


class SupplierService:
    def __init__(
        self,
        session_factory: Callable[[], Session],
    ) -> None:
        self._session_factory = session_factory

    def get_supplier(self, supplier_id: int) -> Supplier | None:
        with self._create_uow() as uow:
            if uow.suppliers is None:
                raise RuntimeError("Unit of Work is not initialized.")

            return uow.suppliers.get_by_id(supplier_id)

    def list_suppliers(self, *, active_only: bool = False) -> list[Supplier]:
        with self._create_uow() as uow:
            if uow.suppliers is None:
                raise RuntimeError("Unit of Work is not initialized.")

            return uow.suppliers.list_all(active_only=active_only)

    def create_supplier(
        self,
        *,
        name: str,
        website_url: str,
    ) -> Supplier:
        with self._create_uow() as uow:
            if uow.suppliers is None:
                raise RuntimeError("Unit of Work is not initialized.")

            existing = uow.suppliers.get_by_name(name)
            if existing is not None:
                raise ConflictError("Supplier with this name already exists.")
            return uow.suppliers.create(
                name=name,
                website_url=website_url,
            )

    def _create_uow(self) -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(self._session_factory)
