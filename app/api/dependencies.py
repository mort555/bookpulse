from collections.abc import Generator

from sqlalchemy.orm import Session

from app.infra.database.session import SessionFactory
from app.infra.database.unit_of_work import SqlAlchemyUnitOfWork
from app.services.supplier_service import SupplierService


def get_session() -> Generator[Session, None, None]:
    session = SessionFactory()

    try:
        yield session
    finally:
        session.close()


def get_supplier_service() -> SupplierService:
    return SupplierService(SessionFactory)


def get_uow() -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(SessionFactory)
