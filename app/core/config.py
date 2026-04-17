from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://shortener:shortener@db:5432/shortener"
    redis_url: str = "redis://redis:6379/0"
    base_url: str = "http://localhost:8000"
    short_code_length: int = 6


@lru_cache
def get_settings() -> Settings:
    return Settings()