from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    debug: bool = False

    database_url: str = Field(
        default="postgresql+psycopg://bookpulse:bookpulse@localhost:5432/bookpulse",
        repr=False,
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        repr=False,
    )

    jwt_secret_key: str = Field(
        default="change-this-secret-key-in-production",
        repr=False,
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()
