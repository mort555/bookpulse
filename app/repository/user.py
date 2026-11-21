from app.models.user import User
from app.schemas.user import UserCreationSchema
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(data: UserCreationSchema, db: AsyncSession) -> User: #dto в папці домейн
    new_user = User(
        username=data.username,
        email=data.email,
        hashed_password=data.password,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


