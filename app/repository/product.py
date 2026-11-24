from app.models.product import Product
from app.repository.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    model = Product

    async def get_by_upc(self, upc: str) -> Product | None:
        return await self.get_one_by(upc=upc)

    async def get_by_title(self, title: str) -> Product | None:
        return await self.get_one_by(title=title)

    async def get_by_category(self, category_id: int) -> list[Product]:
        return await self.get_all_by(category_id=category_id)
