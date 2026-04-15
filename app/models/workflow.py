"""工作流数据模型"""
from datetime import datetime, timezone
from typing import Optional, List, Any

from sqlalchemy import Integer, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database import Base


class Workflow(Base):
    """自动化工作流模型"""

    __tablename__ = "workflows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    test_case_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("test_cases.id"),
        nullable=False,
        unique=True,
        comment="关联的测试用例ID",
    )
    name: Mapped[str] = mapped_column(Text, nullable=True, default="", comment="工作流名称")
    description: Mapped[str] = mapped_column(Text, default="", comment="工作流描述")

    # 步骤流数据（nodes 和 edges）
    nodes: Mapped[List[Any]] = mapped_column(JSON, default=list, comment="节点列表")
    edges: Mapped[List[Any]] = mapped_column(JSON, default=list, comment="边列表")

    # 状态
    is_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="是否启用"
    )
    last_run_status: Mapped[str] = mapped_column(
        Text, default="", comment="最后运行状态"
    )

    # 统计
    total_runs: Mapped[int] = mapped_column(Integer, default=0, comment="总执行次数")
    last_run_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后执行时间"
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="更新时间",
    )

    # 关联
    test_case = relationship("TestCase", back_populates="workflow")
