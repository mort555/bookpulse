from app.models.supplier_price_upload import SupplierPriceUpload
from app.repository.base import BaseRepository


class SupplierPriceUploadRepository(BaseRepository[SupplierPriceUpload]):
    model = SupplierPriceUpload

    async def get_by_supplier_and_hash(
        self, supplier_id: int, file_hash: str
    ) -> SupplierPriceUpload | None:
        return await self.get_one_by(supplier_id=supplier_id, file_hash=file_hash)

    async def get_by_supplier(self, supplier_id: int) -> list[SupplierPriceUpload]:
        return await self.get_all_by(supplier_id=supplier_id)
