from app.models.supplier import Supplier
from app.repository.base import BaseRepository


class SupplierRepository(BaseRepository[Supplier]):
    model = Supplier

    async def get_by_email(self, email: str) -> Supplier | None:
        return await self.get_one_by(email=email)

    async def get_active(self) -> list[Supplier]:
        return await self.get_all_by(is_active=True)
