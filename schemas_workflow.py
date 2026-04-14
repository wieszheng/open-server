"""工作流 Pydantic Schemas"""
from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field


class WorkflowBase(BaseModel):
    """工作流基础 Schema"""
    name: str = Field(..., description="工作流名称")
    description: str = Field(default="", description="工作流描述")
    nodes: List[Any] = Field(default_factory=list, description="节点列表")
    edges: List[Any] = Field(default_factory=list, description="边列表")


class WorkflowCreate(WorkflowBase):
    """创建工作流请求"""
    pass


class WorkflowUpdate(BaseModel):
    """更新工作流请求"""
    name: Optional[str] = Field(None, description="工作流名称")
    description: Optional[str] = Field(None, description="工作流描述")
    nodes: Optional[List[Any]] = Field(None, description="节点列表")
    edges: Optional[List[Any]] = Field(None, description="边列表")
    is_enabled: Optional[int] = Field(None, description="是否启用")


class WorkflowResponse(WorkflowBase):
    """工作流响应"""
    id: int
    test_case_id: int
    is_enabled: int
    last_run_status: str
    total_runs: int
    last_run_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkflowResponseOptional(BaseModel):
    """可选的工作流响应（用于 GET，检查是否存在）"""
    id: Optional[int] = None
    test_case_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    nodes: Optional[List[Any]] = None
    edges: Optional[List[Any]] = None
    is_enabled: Optional[int] = None
    last_run_status: Optional[str] = None
    total_runs: Optional[int] = None
    last_run_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
