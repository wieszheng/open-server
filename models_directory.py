"""目录/项目目录 Model"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime

from database import Base


class Directory(Base):
    """目录模型 - 用于组织测试用例"""
    __tablename__ = "directories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True, comment="目录名称")
    description = Column(Text, default="", comment="目录描述")
    icon = Column(String(50), default="folder", comment="图标名称")
    color = Column(String(20), default="blue", comment="颜色主题")
    
    # 排序和状态
    sort_order = Column(Integer, default=0, comment="排序顺序")
    is_default = Column(Boolean, default=False, comment="是否为默认目录")
    
    # 统计（冗余字段，用于快速查询）
    case_count = Column(Integer, default=0, comment="用例数量")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
