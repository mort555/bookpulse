from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from app.core.config import get_settings
from app.database.session import get_db
from app.models.user import User
from app.repository.user import get_user_by_email
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt  # type: ignore[import-untyped]
from sqlalchemy.ext.asyncio import AsyncSession

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
oauth2_token_dependency = Depends(oauth2_scheme)
db_session_dependency = Depends(get_db)


class Auth:
    settings = get_settings()
    SECRET_KEY = settings.jwt_secret_key
    ALGORITHM = settings.jwt_algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
    REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days
    EMAIL_TOKEN_EXPIRE_DAYS = settings.email_token_expire_days

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8")[:72],
            hashed_password.encode("utf-8"),
        )

    def get_password_hash(self, password: str) -> str:
        return bcrypt.hashpw(
            password.encode("utf-8")[:72],
            bcrypt.gensalt(),
        ).decode("utf-8")

    def _create_token(
        self, data: dict[str, Any], expires_delta: timedelta, scope: str
    ) -> str:
        to_encode = data.copy()
        expire = datetime.now(UTC) + expires_delta
        to_encode.update(
            {
                "iat": datetime.now(UTC),
                "exp": expire,
                "scope": scope,
            }
        )
        token: str = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return token

    def _decode_token(
        self, token: str, expected_scope: str | None = None
    ) -> dict[str, Any]:
        try:
            payload: dict[str, Any] = jwt.decode(
                token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if expected_scope and payload.get("scope") != expected_scope:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid scope for token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return payload
        except JWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

    async def create_access_token(self, data: dict[str, Any]) -> str:
        return self._create_token(
            data=data,
            expires_delta=timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES),
            scope="access_token",
        )

    async def create_refresh_token(self, data: dict[str, Any]) -> str:
        return self._create_token(
            data=data,
            expires_delta=timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS),
            scope="refresh_token",
        )

    async def create_email_token(self, data: dict[str, Any]) -> str:
        return self._create_token(
            data=data,
            expires_delta=timedelta(days=self.EMAIL_TOKEN_EXPIRE_DAYS),
            scope="email_token",
        )

    async def decode_email_token(self, token: str) -> str:
        payload = self._decode_token(token, expected_scope="email_token")
        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject:
            raise self._invalid_credentials()
        return subject

    async def decode_refresh_token(self, refresh_token: str) -> str:
        payload = self._decode_token(refresh_token, expected_scope="refresh_token")
        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject:
            raise self._invalid_credentials()
        return subject

    async def authenticate_user(
        self,
        token: str = oauth2_token_dependency,
        db: AsyncSession = db_session_dependency,
    ) -> User:
        payload = self._decode_token(token, expected_scope="access_token")
        email = payload.get("sub")
        if not isinstance(email, str) or not email:
            raise self._invalid_credentials()

        user = await get_user_by_email(email, db)
        if user is None or not user.is_active:
            raise self._invalid_credentials()
        return user

    @staticmethod
    def _invalid_credentials() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


auth_service = Auth()