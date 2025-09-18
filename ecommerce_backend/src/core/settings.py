import os
from typing import List


class Settings:
    """
    Application settings loaded from environment variables.
    Do not read .env directly; the orchestrator will provide env vars.
    """
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")
    SITE_URL: str = os.getenv("SITE_URL", "http://localhost:3000")
    PAYMENT_PROVIDER: str = os.getenv("PAYMENT_PROVIDER", "mock")
    PAYMENT_PROVIDER_API_KEY: str = os.getenv("PAYMENT_PROVIDER_API_KEY", "")
    CORS_ALLOW_ORIGINS: List[str] = os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")


settings = Settings()
