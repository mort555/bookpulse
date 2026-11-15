from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordRequestForm,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger  # Використовуємо твій існуючий модуль логування
from app.database.session import get_db
from app.repository import user as repositories_users
from app.schemas.user import TokenSchema, UserCreationSchema, UserResponseSchema
from app.services.auth import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

# Модуль-левельні синглтони для залежностей (уникнення викликів функцій у дефолтах аргументів)
get_refresh_token = HTTPBearer()

DbSessionDep = Depends(get_db)
OAuth2FormDep = Depends(OAuth2PasswordRequestForm)
RefreshAuthDep = Depends(get_refresh_token)


@router.post(
    "/signup", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserCreationSchema, request: Request, db: AsyncSession = DbSessionDep
):
    exist_user = await repositories_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repositories_users.create_user(body, db)
    logger.info(f"User {new_user.email} created")  # type: ignore
    return new_user


@router.post("/login", response_model=TokenSchema)
async def login(
    body: OAuth2PasswordRequestForm = OAuth2FormDep, db: AsyncSession = DbSessionDep
):
    user = await repositories_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is banned and cannot log in",
        )

    # ВИПРАВЛЕННЯ: замість user.password використовуємо user.hashed_password
    if not auth_service.verify_password(body.password, user.hashed_password):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )

    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repositories_users.update_token(user, refresh_token, db)  # type: ignore
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/refresh_token", response_model=TokenSchema)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = RefreshAuthDep,
    db: AsyncSession = DbSessionDep,
):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await auth_service.create_access_token(data={"sub": email})
    new_refresh_token = await auth_service.create_refresh_token(data={"sub": email})

    # Оновлюємо токен через репозиторій, не чіпаючи саму модель
    await repositories_users.update_token(user, new_refresh_token, db)  # type: ignore

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }
