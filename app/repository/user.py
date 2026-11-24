from app.models.user import User
from app.repository.base import BaseRepository
from app.schemas.user import UserCreationSchema
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        return await self.get_one_by(email=email)


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    return await UserRepository(db).get_by_email(email)


async def create_user(data: UserCreationSchema, db: AsyncSession) -> User:
    new_user = User(
        username=data.username,
        email=data.email,
        hashed_password=data.password,
    )
    return await UserRepository(db).create(new_user)

