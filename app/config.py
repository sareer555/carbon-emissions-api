"""Application configuration, loaded from environment variables / .env."""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "SMB Carbon Emissions Calculator API"
    environment: str = "development"  # development | production
    api_prefix: str = "/v1"

    # Database. Defaults to a local SQLite file so the project runs with
    # zero external dependencies out of the box. Point DATABASE_URL at a
    # Postgres instance (Supabase/Neon free tier) for production.
    database_url: str = "sqlite:///./carbon_emissions.db"

    # Rate limiting / usage quotas
    redis_url: Optional[str] = None  # set to use Upstash/Redis instead of in-memory limiter
    burst_limit_per_minute: int = 60  # short-window throttle, applies to every plan

    # Plans: monthly call quota per plan name. Keep in sync with pricing in README.
    plan_quotas: dict = {
        "free": 100,
        "starter": 1000,
        "growth": 10000,
        "scale": 100000,
    }

    # Auth
    admin_bootstrap_token: Optional[str] = None  # optional shared secret for scripts/create_api_key

    disclaimer: str = (
        "This is an estimate for informational purposes only, generated from "
        "publicly published emission factors. It is not a certified carbon "
        "audit and is not a substitute for advice from a licensed "
        "sustainability auditor or legal ESG compliance counsel."
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
