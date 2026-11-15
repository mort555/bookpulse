from app.models.user import User
from app.schemas.user import UserCreationSchema
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(body: UserCreationSchema, db: AsyncSession) -> User:
    new_user = User(
        username=body.username,
        email=body.email,
        hashed_password=body.password,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession) -> None:
    """Оновлення або скидання refresh токена користувача."""
    # Використовуємо setattr або додаємо # type: ignore, щоб Mypy не сварився на атрибут
    user.refresh_token = token # type: ignore
    db.add(user)
    await db.commit()
    await db.refresh(user)
