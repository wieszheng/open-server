"""工作流 CRUD 操作"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models_workflow import Workflow
from models_test_case import TestCase
import schemas_workflow as schemas


async def get_workflow_by_test_case(db: AsyncSession, test_case_id: int) -> Optional[Workflow]:
    """根据测试用例ID获取工作流"""
    result = await db.execute(
        select(Workflow).where(Workflow.test_case_id == test_case_id)
    )
    return result.scalar_one_or_none()


async def get_workflow(db: AsyncSession, workflow_id: int) -> Optional[Workflow]:
    """获取工作流详情"""
    result = await db.execute(
        select(Workflow)
        .options(selectinload(Workflow.test_case))
        .where(Workflow.id == workflow_id)
    )
    return result.scalar_one_or_none()


async def get_workflows(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Workflow]:
    """获取工作流列表"""
    result = await db.execute(
        select(Workflow)
        .options(selectinload(Workflow.test_case))
        .offset(skip)
        .limit(limit)
        .order_by(Workflow.updated_at.desc())
    )
    return list(result.scalars().all())


async def get_workflowed_test_case_ids(db: AsyncSession) -> List[int]:
    """获取已有工作流的所有测试用例ID（用于前端标记"已编排"）"""
    result = await db.execute(select(Workflow.test_case_id))
    return [row[0] for row in result.fetchall()]


async def upsert_flow(
    db: AsyncSession, test_case_id: int, data: schemas.FlowUpsert
) -> Workflow:
    """
    保存 Flow（upsert）：不存在则创建，存在则更新 nodes/edges。
    同步更新测试用例的 is_automated 标记。
    """
    existing = await get_workflow_by_test_case(db, test_case_id)

    # 同步：有 flow 即视为已自动化
    result = await db.execute(select(TestCase).where(TestCase.id == test_case_id))
    test_case = result.scalar_one_or_none()
    if test_case:
        test_case.is_automated = True

    if existing:
        existing.nodes = data.nodes
        existing.edges = data.edges
        existing.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(existing)
        return existing

    workflow = Workflow(
        test_case_id=test_case_id,
        nodes=data.nodes,
        edges=data.edges,
    )
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)
    return workflow


async def update_workflow(
    db: AsyncSession, workflow_id: int, data: schemas.WorkflowUpdate
) -> Optional[Workflow]:
    """更新工作流（管理接口）"""
    workflow = await get_workflow(db, workflow_id)
    if not workflow:
        return None

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(workflow, key, value)

    workflow.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(workflow)
    return workflow


async def delete_workflow(db: AsyncSession, workflow_id: int) -> bool:
    """删除工作流，同步取消测试用例的自动化标记"""
    workflow = await get_workflow(db, workflow_id)
    if not workflow:
        return False

    test_case_id = workflow.test_case_id
    await db.delete(workflow)

    result = await db.execute(select(TestCase).where(TestCase.id == test_case_id))
    test_case = result.scalar_one_or_none()
    if test_case:
        test_case.is_automated = False

    await db.commit()
    return True
