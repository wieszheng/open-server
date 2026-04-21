"""测试执行数据模型"""
from datetime import datetime, timezone
from typing import Any, List, Optional

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TestExecution(Base):
    """测试执行记录模型 — 每个测试用例只保留最新一次执行（upsert by test_case_id）"""

    __tablename__ = "test_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    duration: Mapped[float] = mapped_column(Float, nullable=False, comment="总耗时(秒)")
    total_cases: Mapped[int] = mapped_column(Integer, default=0)
    passed_cases: Mapped[int] = mapped_column(Integer, default=0)
    failed_cases: Mapped[int] = mapped_column(Integer, default=0)

    test_case_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("test_cases.id", ondelete="CASCADE"),
        nullable=True, index=True, comment="关联测试用例ID"
    )

    # [{node_id, label, success, message, duration, screenshot}]
    node_results: Mapped[List[Any]] = mapped_column(
        JSON, default=list, comment="节点执行结果列表（含截图base64）"
    )
