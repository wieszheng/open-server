"""工作流 Pydantic Schemas"""
from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field


# ===================== /test-cases/{id}/flow 接口专用 =====================

class FlowUpsert(BaseModel):
    """保存工作流请求（前端只关心 nodes/edges）"""
    nodes: List[Any] = Field(default_factory=list, description="节点列表")
    edges: List[Any] = Field(default_factory=list, description="边列表")


class FlowResponse(BaseModel):
    """工作流响应（精简，面向前端）"""
    nodes: List[Any]
    edges: List[Any]
    updated_at: datetime

    class Config:
        from_attributes = True


# ===================== /workflows 管理接口（内部/调试用） =====================

class WorkflowResponse(BaseModel):
    """完整工作流响应（管理接口）"""
    id: int
    test_case_id: int
    name: str
    description: str
    nodes: List[Any]
    edges: List[Any]
    is_enabled: bool
    last_run_status: str
    total_runs: int
    last_run_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkflowUpdate(BaseModel):
    """更新工作流请求（管理接口）"""
    name: Optional[str] = None
    description: Optional[str] = None
    nodes: Optional[List[Any]] = None
    edges: Optional[List[Any]] = None
    is_enabled: Optional[bool] = None
