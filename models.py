"""数据库模型"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Integer, Float, Boolean, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Script(Base):
    """脚本模型"""
    __tablename__ = "scripts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    code: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(50), default="api")
    author: Mapped[str] = mapped_column(String(100), default="未知")
    tags: Mapped[str] = mapped_column(JSON, default=list)  # 存储为 JSON 数组
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    downloads: Mapped[int] = mapped_column(Integer, default=0)
    views: Mapped[int] = mapped_column(Integer, default=0)
    featured: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TestExecution(Base):
    """测试执行记录模型"""
    __tablename__ = "test_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    duration: Mapped[float] = mapped_column(Float, nullable=False)  # 执行耗时（秒）
    total_cases: Mapped[int] = mapped_column(Integer, default=0)
    passed_cases: Mapped[int] = mapped_column(Integer, default=0)
    failed_cases: Mapped[int] = mapped_column(Integer, default=0)
    environment: Mapped[str] = mapped_column(String(100), default="production")
