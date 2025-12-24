import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    BOT_TOKEN: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    MEILI_HOST: str = "meilisearch"
    MEILI_PORT: str = "7700"
    MEILI_MASTER_KEY: str = ""
    MEILI_ENV: str = "development"
    WEBAPP_URL: str = "http://localhost:8000"
    ALLOWED_ORIGINS: str = "*"  # Comma-separated list for production

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
    )


settings = Settings()
