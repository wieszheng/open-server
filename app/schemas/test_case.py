"""测试用例 Pydantic Schemas"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TestCaseBase(BaseModel):
    """测试用例基础 schema"""

    name: str = Field(..., max_length=200, description="用例名称")
    description: str = Field(default="", description="用例描述")
    case_type: str = Field(
        default="api", description="用例类型: api/ui/e2e/unit/perf"
    )
    priority: str = Field(default="P2", description="优先级: P0/P1/P2/P3")
    status: str = Field(
        default="active", description="状态: active/deprecated/draft"
    )
    module: str = Field(default="", description="所属模块")
    directory_id: Optional[int] = Field(None, description="所属目录ID")
    preconditions: str = Field(default="", description="前置条件")
    test_steps: str = Field(default="", description="测试步骤")
    expected_results: str = Field(default="", description="预期结果")
    author: str = Field(default="未知", max_length=100, description="创建者")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    script_id: Optional[int] = Field(None, description="关联脚本ID")
    is_parallel: bool = Field(default=True, description="是否可并行")


class TestCaseCreate(TestCaseBase):
    """创建测试用例 schema"""

    pass


class TestCaseUpdate(BaseModel):
    """更新测试用例 schema（所有字段可选）"""

    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    case_type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    module: Optional[str] = None
    preconditions: Optional[str] = None
    test_steps: Optional[str] = None
    expected_results: Optional[str] = None
    author: Optional[str] = None
    tags: Optional[List[str]] = None
    script_id: Optional[int] = None
    is_parallel: Optional[bool] = None


class TestCaseResponse(TestCaseBase):
    """测试用例响应 schema"""

    id: int
    is_automated: bool = False  # 只读：由工作流编排状态驱动
    total_runs: int = 0
    passed_runs: int = 0
    failed_runs: int = 0
    pass_rate: float = 0.0
    avg_duration: float = 0.0
    last_run_time: Optional[datetime] = None
    flaky: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
