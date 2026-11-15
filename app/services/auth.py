from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from fastapi import HTTPException, status

# Якщо у тебе налаштовані константи у проєкті (наприклад, через pydantic-settings),
# імпортуй їх з app.core.config. Якщо ні — використовуються дефолтні значення нижче.
SECRET_KEY = "your-super-secret-key-change-it"  # Бажано брати з settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


class AuthService:
    def get_password_hash(self, password: str) -> str:
        # Обрізаємо пароль рівно до 72 байтів (технічне обмеження bcrypt)
        pwd_bytes = password.encode("utf-8")[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed.decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pwd_bytes = plain_password.encode("utf-8")[:72]
        return bcrypt.checkpw(pwd_bytes, hashed_password.encode("utf-8"))

    async def create_access_token(
        self, data: dict, expires_delta: timedelta | None = None
    ) -> str:
        to_encode = data.copy()
        expire = datetime.now(UTC) + (
            expires_delta
            if expires_delta
            else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    async def create_refresh_token(
        self, data: dict, expires_delta: timedelta | None = None
    ) -> str:
        to_encode = data.copy()
        expire = datetime.now(UTC) + (
            expires_delta
            if expires_delta
            else timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    async def decode_refresh_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                )
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                )
            return email
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )


# Глобальний інстанс сервісу
auth_service = AuthService()
