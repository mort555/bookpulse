from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db  # залежність вашої сесії БД
from app.models.users import User  # ваша модель користувача

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    """Перевіряє access-токен та повертає поточного користувача з БД."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Тут виконується decode вашого JWT access-токена (отримання user_id / email)
    # Наприклад, за допомогою PyJWT або python-jose:
    # payload = decode_access_token(token)
    # user_id = payload.get("sub")
    # if user_id is None: raise credentials_exception

    # Приклад пошуку в БД:
    # user = await db.get(User, int(user_id))
    # if user is None or not user.is_active: raise credentials_exception
    # return user
    pass


def require_role(required_role: str):
    """Фабрика залежностей для перевірки ролі користувача (RBAC)."""

    async def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:  # адаптуйте під вашу логіку ролей
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for this role",
            )
        return current_user

    return role_dependency
