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

    app_name: str = "BookPulse"
    app_version: str = "0.1.0"
    debug: bool = False

    api_v1_prefix: str = "/api/v1"

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

    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
