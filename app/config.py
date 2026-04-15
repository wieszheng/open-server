"""应用配置"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置设置"""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./scripts.db",
        description="数据库连接URL",
    )
    APP_NAME: str = Field(default="Script Market API", description="应用名称")
    DEBUG: bool = Field(default=True, description="调试模式")
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="允许的CORS源",
    )


settings = Settings()
