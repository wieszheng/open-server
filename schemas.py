"""Pydantic Schemas"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ===================== Script Schemas =====================

class ScriptBase(BaseModel):
    """脚本基础 schema"""
    name: str = Field(..., max_length=200, description="脚本名称")
    description: str = Field(default="", description="脚本描述")
    code: str = Field(default="", description="脚本代码")
    category: str = Field(default="api", max_length=50, description="分类")
    author: str = Field(default="未知", max_length=100, description="作者")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    featured: bool = Field(default=False, description="是否精选")


class ScriptCreate(ScriptBase):
    """创建脚本 schema"""
    pass


class ScriptUpdate(BaseModel):
    """更新脚本 schema（所有字段可选）"""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    code: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    author: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    featured: Optional[bool] = None


class ScriptResponse(ScriptBase):
    """脚本响应 schema"""
    id: int
    rating: float = 0.0
    downloads: int = 0
    views: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===================== TestExecution Schemas =====================

class TestExecutionBase(BaseModel):
    """测试执行基础 schema"""
    duration: float = Field(..., description="执行耗时（秒）")
    total_cases: int = Field(default=0, description="总用例数")
    passed_cases: int = Field(default=0, description="通过用例数")
    failed_cases: int = Field(default=0, description="失败用例数")
    environment: str = Field(default="production", max_length=100, description="环境")


class TestExecutionCreate(TestExecutionBase):
    """创建测试执行记录 schema"""
    pass


class TestExecutionResponse(TestExecutionBase):
    """测试执行响应 schema"""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# ===================== Console Stats Schemas =====================

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


# ===================== TestCase Schemas =====================

class TestCaseBase(BaseModel):
    """测试用例基础 schema"""
    name: str = Field(..., max_length=200, description="用例名称")
    description: str = Field(default="", description="用例描述")
    case_type: str = Field(default="api", description="用例类型: api/ui/e2e/unit/perf")
    priority: str = Field(default="P2", description="优先级: P0/P1/P2/P3")
    status: str = Field(default="active", description="状态: active/deprecated/draft")
    module: str = Field(default="", description="所属模块")
    directory_id: Optional[int] = Field(None, description="所属目录ID")
    preconditions: str = Field(default="", description="前置条件")
    test_steps: str = Field(default="", description="测试步骤")
    expected_results: str = Field(default="", description="预期结果")
    author: str = Field(default="未知", max_length=100, description="创建者")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    script_id: Optional[int] = Field(None, description="关联脚本ID")
    is_automated: bool = Field(default=False, description="是否自动化")
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
    is_automated: Optional[bool] = None
    is_parallel: Optional[bool] = None


class TestCaseResponse(TestCaseBase):
    """测试用例响应 schema"""
    id: int
    total_runs: int = 0
    passed_runs: int = 0
    failed_runs: int = 0
    pass_rate: float = 0.0
    avg_duration: float = 0.0
    last_run_time: Optional[datetime] = None
    flaky: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===================== Directory Schemas =====================

class DirectoryBase(BaseModel):
    """目录基础 schema"""
    name: str = Field(..., max_length=100, description="目录名称")
    description: str = Field(default="", description="目录描述")
    icon: str = Field(default="folder", max_length=50, description="图标名称")
    color: str = Field(default="blue", max_length=20, description="颜色主题")
    sort_order: int = Field(default=0, description="排序顺序")
    parent_id: Optional[int] = Field(None, description="父目录ID")


class DirectoryCreate(DirectoryBase):
    """创建目录 schema"""
    pass


class DirectoryUpdate(BaseModel):
    """更新目录 schema"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=20)
    sort_order: Optional[int] = None
    parent_id: Optional[int] = Field(None, description="父目录ID")


class DirectoryResponse(DirectoryBase):
    """目录响应 schema"""
    id: int
    case_count: int = 0
    is_default: bool = False
    created_at: datetime
    updated_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
