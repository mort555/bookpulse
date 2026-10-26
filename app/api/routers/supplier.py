from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_supplier_service
from app.api.schemas.supplier import SupplierCreate, SupplierRead
from app.core.exceptions import NotFoundError
from app.services.supplier_service import SupplierService

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.get("", response_model=list[SupplierRead])
def list_suppliers(
    service: Annotated[SupplierService, Depends(get_supplier_service)],
    active_only: Annotated[bool, Query()] = False,
) -> list[SupplierRead]:
    suppliers = service.list_suppliers(active_only=active_only)
    return [SupplierRead.model_validate(supplier) for supplier in suppliers]


@router.get("/{supplier_id}", response_model=SupplierRead)
def get_supplier(
    supplier_id: int,
    service: Annotated[SupplierService, Depends(get_supplier_service)],
) -> SupplierRead:
    supplier = service.get_supplier(supplier_id)

    if supplier is None:
        raise NotFoundError("Supplier not found.")

    return SupplierRead.model_validate(supplier)


@router.post(
    "",
    response_model=SupplierRead,
    status_code=status.HTTP_201_CREATED,
)
def create_supplier(
    payload: SupplierCreate,
    service: Annotated[SupplierService, Depends(get_supplier_service)],
) -> SupplierRead:
    supplier = service.create_supplier(
        name=payload.name,
        website_url=str(payload.website_url),
    )
    return SupplierRead.model_validate(supplier)
