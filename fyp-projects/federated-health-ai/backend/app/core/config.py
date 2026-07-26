"""Application settings, environment-driven."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FHA_", env_file=".env", extra="ignore")

    app_name: str = "federated-health-ai"
    database_url: str = "sqlite:///./fha.db"
    secret_key: str = "change-me-in-production-4f8a2c91"
    access_token_expire_minutes: int = 60 * 8
    algorithm: str = "HS256"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    # Federated cohort configuration (synthetic data seed shared by all services)
    cohort_seed: int = 42
    cohort_test_samples: int = 1500


@lru_cache
def get_settings() -> Settings:
    return Settings()
