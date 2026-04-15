"""测试执行数据模型"""
from datetime import datetime, timezone

from sqlalchemy import String, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TestExecution(Base):
    """测试执行记录模型"""

    __tablename__ = "test_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    duration: Mapped[float] = mapped_column(Float, nullable=False)
    total_cases: Mapped[int] = mapped_column(Integer, default=0)
    passed_cases: Mapped[int] = mapped_column(Integer, default=0)
    failed_cases: Mapped[int] = mapped_column(Integer, default=0)
    environment: Mapped[str] = mapped_column(String(100), default="production")
