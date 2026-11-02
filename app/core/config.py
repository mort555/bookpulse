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

    postgres_db: str = Field(
        default="bookpulse",
        repr=False,
    )
    postgres_user: str = Field(
        default="bookpulse",
        repr=False,
    )

    postgres_password: str = Field(
        default="bookpulse",
        repr=False,
    )
    postgres_port: int = Field(
        default=5433,
        repr=False,
    )
    postgres_host: str = Field(
        default="localhost",
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

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
