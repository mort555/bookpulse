from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.database.models import Supplier


class SupplierRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, supplier_id: int) -> Supplier | None:
        statement = select(Supplier).where(Supplier.id == supplier_id)
        return self._session.scalar(statement)

    def get_by_name(self, name: str) -> Supplier | None:
        statement = select(Supplier).where(Supplier.name == name)
        return self._session.scalar(statement)

    def list_all(self, *, active_only: bool = False) -> list[Supplier]:
        statement = select(Supplier).order_by(Supplier.id)

        if active_only:
            statement = statement.where(Supplier.is_active.is_(True))

        return list(self._session.scalars(statement).all())

    def create(
        self,
        *,
        name: str,
        website_url: str,
        is_active: bool = True,
    ) -> Supplier:
        supplier = Supplier(
            name=name,
            website_url=website_url,
            is_active=is_active,
        )

        self._session.add(supplier)
        self._session.flush()

        return supplier
