"""工作流/自动化编排模型"""
from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship

from database import Base


class Workflow(Base):
    """自动化工作流模型"""
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False, unique=True, comment="关联的测试用例ID")
    name = Column(Text, nullable=True, default="", comment="工作流名称")
    description = Column(Text, default="", comment="工作流描述")

    # 步骤流数据（nodes 和 edges）
    nodes = Column(JSON, default=list, comment="节点列表")
    edges = Column(JSON, default=list, comment="边列表")

    # 状态
    is_enabled = Column(Boolean, default=True, comment="是否启用")
    last_run_status = Column(Text, default="", comment="最后运行状态")

    # 统计
    total_runs = Column(Integer, default=0, comment="总执行次数")
    last_run_time = Column(DateTime, nullable=True, comment="最后执行时间")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联
    test_case = relationship("TestCase", backref="workflow", foreign_keys=[test_case_id])
