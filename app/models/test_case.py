"""测试用例数据模型"""
from datetime import datetime, timezone
from typing import Optional
import enum

from sqlalchemy import String, Integer, Float, Boolean, Text, DateTime, ForeignKey, Enum, Column
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database import Base


class CasePriority(str, enum.Enum):
    """用例优先级"""

    P0 = "P0"  # 核心功能
    P1 = "P1"  # 重要功能
    P2 = "P2"  # 一般功能
    P3 = "P3"  # 低优先级


class CaseStatus(str, enum.Enum):
    """用例状态"""

    ACTIVE = "active"  # 活跃
    DEPRECATED = "deprecated"  # 已废弃
    DRAFT = "draft"  # 草稿


class CaseType(str, enum.Enum):
    """用例类型"""

    API = "api"  # 接口测试
    UI = "ui"  # UI测试
    E2E = "e2e"  # 端到端测试
    UNIT = "unit"  # 单元测试
    PERFORMANCE = "perf"  # 性能测试


class TestCase(Base):
    """测试用例模型"""

    __tablename__ = "test_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True, comment="用例名称"
    )
    description: Mapped[str] = mapped_column(Text, default="", comment="用例描述")

    # 用例类型和优先级
    case_type: Mapped[CaseType] = mapped_column(
        Enum(CaseType), default=CaseType.API, comment="用例类型"
    )
    priority: Mapped[CasePriority] = mapped_column(
        Enum(CasePriority), default=CasePriority.P2, comment="优先级"
    )
    status: Mapped[CaseStatus] = mapped_column(
        Enum(CaseStatus), default=CaseStatus.ACTIVE, comment="状态"
    )

    # 关联信息
    script_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("scripts.id"), nullable=True, comment="关联脚本ID"
    )
    directory_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("directories.id"), nullable=True, comment="所属目录ID"
    )
    module: Mapped[str] = mapped_column(
        String(100), default="", comment="所属模块"
    )

    # 执行信息
    preconditions: Mapped[str] = mapped_column(
        Text, default="", comment="前置条件"
    )
    test_steps: Mapped[str] = mapped_column(Text, default="", comment="测试步骤")
    expected_results: Mapped[str] = mapped_column(
        Text, default="", comment="预期结果"
    )

    # 统计数据
    author: Mapped[str] = mapped_column(String(100), default="未知", comment="创建者")
    tags: Mapped[str] = mapped_column(
        String(500), default="", comment="标签，逗号分隔"
    )
    rating: Mapped[float] = mapped_column(Float, default=5.0, comment="评分")

    # 执行统计
    total_runs: Mapped[int] = mapped_column(Integer, default=0, comment="总执行次数")
    passed_runs: Mapped[int] = mapped_column(Integer, default=0, comment="通过次数")
    failed_runs: Mapped[int] = mapped_column(Integer, default=0, comment="失败次数")
    last_run_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后执行时间"
    )
    avg_duration: Mapped[float] = mapped_column(
        Float, default=0.0, comment="平均执行时长(秒)"
    )

    # 标记
    is_automated: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否自动化"
    )
    is_parallel: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="是否可并行"
    )
    flaky: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否不稳定"
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
    workflow = relationship("Workflow", back_populates="test_case", uselist=False)

    def get_tags_list(self) -> list[str]:
        """获取标签列表"""
        return [t.strip() for t in self.tags.split(",") if t.strip()]

    def get_pass_rate(self) -> float:
        """计算通过率"""
        if self.total_runs == 0:
            return 0.0
        return round(self.passed_runs / self.total_runs * 100, 1)
