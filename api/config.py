"""
Application configuration.
"""
import secrets
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/bankrot"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_TOKEN: str = "change-me-in-production"  # For bot-to-API auth
    
    # JWT Authentication
    SECRET_KEY: str = secrets.token_urlsafe(32)  # Override in .env!
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # OpenAI (for AI features)
    OPENAI_API_KEY: str = ""
    
    # Redis (for caching, rate limiting)
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Security
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8501"]
    
    # Encryption key for sensitive data (32 bytes base64)
    # Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
    ENCRYPTION_KEY: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
