from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    StrtOS Enterprise Centralized Environment Configuration.
    Validates required secrets and automatically constructs connection strings.
    """
    # APPLICATION
    APP_NAME: str = "StrtOS"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"
    API_V1_STR: str = "/api/v1"
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 5173
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # DATABASE (PostgreSQL)
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "strtos_db"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"
    DATABASE_URL: Optional[str] = None

    # REDIS
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    REDIS_URL: Optional[str] = None

    # JWT SECURITY
    JWT_SECRET_KEY: str = Field(default="strtos-enterprise-secret-key-change-in-prod-2026")
    JWT_REFRESH_SECRET: str = Field(default="strtos-enterprise-refresh-secret-key-change-in-prod-2026")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AI PROVIDERS (LLM ROUTER)
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    QWEN_API_KEY: str = ""

    # TOOLS
    FIRECRAWL_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    SERPER_API_KEY: str = ""
    GOOGLE_PAGESPEED_API_KEY: str = ""
    GOOGLE_MAPS_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=(".env.development", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values) -> str:
        if isinstance(v, str) and v.strip():
            return v
        data = values.data
        host = data.get("DATABASE_HOST", "localhost")
        port = data.get("DATABASE_PORT", 5432)
        user = data.get("DATABASE_USER", "postgres")
        pwd = data.get("DATABASE_PASSWORD", "postgres")
        name = data.get("DATABASE_NAME", "strtos_db")
        return f"postgresql+asyncpg://{user}:{pwd}@{host}:{port}/{name}"

    @field_validator("REDIS_URL", mode="before")
    def assemble_redis_connection(cls, v: Optional[str], values) -> str:
        if isinstance(v, str) and v.strip():
            return v
        data = values.data
        host = data.get("REDIS_HOST", "localhost")
        port = data.get("REDIS_PORT", 6379)
        db = data.get("REDIS_DB", 0)
        pwd = data.get("REDIS_PASSWORD", "")
        auth = f":{pwd}@" if pwd else ""
        return f"redis://{auth}{host}:{port}/{db}"

settings = Settings()

# Fail-fast validation check for production readiness
if settings.APP_ENV == "production":
    if not settings.JWT_SECRET_KEY or "change-in-prod" in settings.JWT_SECRET_KEY:
        raise ValueError("CRITICAL CONFIGURATION ERROR: Production JWT_SECRET_KEY must be configured securely in .env.")
    if not settings.DATABASE_URL:
        raise ValueError("CRITICAL CONFIGURATION ERROR: Production DATABASE_URL is missing.")
