"""应用配置"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./scripts.db"
    APP_NAME: str = "Script Market API"
    DEBUG: bool = True


settings = Settings()
