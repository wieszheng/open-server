"""目录 Pydantic Schemas"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


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

    model_config = {"from_attributes": True}
