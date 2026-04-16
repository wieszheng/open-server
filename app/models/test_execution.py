"""测试执行数据模型"""
from datetime import datetime, timezone
from typing import Any, List, Optional

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TestExecution(Base):
    """测试执行记录模型"""

    __tablename__ = "test_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
    duration: Mapped[float] = mapped_column(Float, nullable=False, comment="总耗时(秒)")
    total_cases: Mapped[int] = mapped_column(Integer, default=0)
    passed_cases: Mapped[int] = mapped_column(Integer, default=0)
    failed_cases: Mapped[int] = mapped_column(Integer, default=0)
    environment: Mapped[str] = mapped_column(String(100), default="default")

    # 关联测试用例
    test_case_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("test_cases.id", ondelete="SET NULL"),
        nullable=True, index=True, comment="关联测试用例ID"
    )

    # 节点级执行结果
    # [{node_id, label, success, message, duration}]
    node_results: Mapped[List[Any]] = mapped_column(
        JSON, default=list, comment="节点执行结果列表"
    )
