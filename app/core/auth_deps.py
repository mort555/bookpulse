from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.repository import user as repositories_users
from app.services.auth import auth_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Оголошуємо залежності як тип через Annotated (лінтер більше не лається на B008)
TokenDep = Annotated[str, Depends(oauth2_scheme)]
DbSessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(token: TokenDep, db: DbSessionDep) -> User:
    """Перевіряє access-токен та повертає поточного користувача з БД."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Декодуємо токен та отримуємо email (sub)
    email = await auth_service.decode_access_token(token) # type: ignore
    if not email:
        raise credentials_exception

    # 2. Шукаємо користувача в базі даних через репозиторій
    user = await repositories_users.get_user_by_email(email, db) # type: ignore
    if user is None or not user.is_active:
        raise credentials_exception

    return user


def require_role(required_role: str):
    """Фабрика залежностей для перевірки ролі користувача (RBAC)."""

    async def role_dependency(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for this role",
            )
        return current_user

    return role_dependency
