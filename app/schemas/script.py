"""脚本 Pydantic Schemas"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


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

    model_config = {"from_attributes": True}
