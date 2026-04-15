"""目录数据模型"""
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import String, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Directory(Base):
    """目录模型 - 用于组织测试用例，支持层级结构"""

    __tablename__ = "directories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, comment="目录名称"
    )
    description: Mapped[str] = mapped_column(Text, default="", comment="目录描述")
    icon: Mapped[str] = mapped_column(String(50), default="folder", comment="图标名称")
    color: Mapped[str] = mapped_column(
        String(20), default="blue", comment="颜色主题"
    )

    # 层级结构
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("directories.id"), nullable=True, comment="父目录ID"
    )

    # 排序和状态
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序顺序")
    is_default: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否为默认目录"
    )

    # 统计（冗余字段，用于快速查询）
    case_count: Mapped[int] = mapped_column(Integer, default=0, comment="用例数量")

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

    # 关联关系
    children: Mapped[List["Directory"]] = relationship(
        "Directory", backref="parent", remote_side=[id], lazy="select"
    )
