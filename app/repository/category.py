from app.models.category import Category
from app.repository.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    model = Category

    async def get_by_slug(self, slug: str) -> Category | None:
        return await self.get_one_by(slug=slug)

    async def get_by_name(self, name: str) -> Category | None:
        return await self.get_one_by(name=name)
