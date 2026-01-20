from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://bankrot:password@localhost:5432/bankrot"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "change_me_32_char_secret_key_here"

    # AI Provider
    AI_PROVIDER: str = "timeweb"
    TIMEWEB_API_KEY: str = ""
    TIMEWEB_API_URL: str = "https://api.timeweb.cloud/v1"
    YANDEXGPT_API_KEY: str = ""
    YANDEXGPT_FOLDER_ID: str = ""


settings = Settings()
