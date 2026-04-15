"""控制台 Pydantic Schemas"""
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class TestExecutionBase(BaseModel):
    """测试执行基础 schema"""

    duration: float = Field(..., description="执行耗时（秒）")
    total_cases: int = Field(default=0, description="总用例数")
    passed_cases: int = Field(default=0, description="通过用例数")
    failed_cases: int = Field(default=0, description="失败用例数")
    environment: str = Field(
        default="production", max_length=100, description="环境"
    )


class TestExecutionCreate(TestExecutionBase):
    """创建测试执行记录 schema"""

    pass


class TestExecutionResponse(TestExecutionBase):
    """测试执行响应 schema"""

    id: int
    timestamp: datetime

    model_config = {"from_attributes": True}


class TestDurationTrend(BaseModel):
    """测试耗时趋势"""

    date: str
    avg_duration: float
    min_duration: float
    max_duration: float
    total_executions: int


class ConsoleStats(BaseModel):
    """控制台统计"""

    total_tests: int
    total_cases: int
    passed_cases: int
    failed_cases: int
    avg_duration: float
    trend: List[TestDurationTrend]
