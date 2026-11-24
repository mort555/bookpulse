from app.database.base import Base
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository[ModelType: Base]:
    model: type[ModelType]

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, object_id: int) -> ModelType | None:
        return await self.db.get(self.model, object_id)

    async def get_all(self) -> list[ModelType]:
        result = await self.db.scalars(select(self.model).order_by("id"))
        return list(result.all())

    async def get_one_by(self, **filters: object) -> ModelType | None:
        result = await self.db.scalars(select(self.model).filter_by(**filters))
        return result.first()

    async def get_all_by(self, **filters: object) -> list[ModelType]:
        statement = select(self.model).filter_by(**filters).order_by("id")
        result = await self.db.scalars(statement)
        return list(result.all())

    async def create(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: ModelType) -> ModelType:
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: ModelType) -> None:
        await self.db.delete(obj)
        await self.db.commit()
