from app.models.supplier_price import SupplierPrice
from app.repository.base import BaseRepository
from sqlalchemy import select


class SupplierPriceRepository(BaseRepository[SupplierPrice]):
    model = SupplierPrice

    async def get_by_supplier_and_product(
        self, supplier_id: int, product_id: int
    ) -> list[SupplierPrice]:
        statement = (
            select(SupplierPrice)
            .where(
                SupplierPrice.supplier_id == supplier_id,
                SupplierPrice.product_id == product_id,
            )
            .order_by(SupplierPrice.valid_from.desc())
        )
        result = await self.db.scalars(statement)
        return list(result.all())
