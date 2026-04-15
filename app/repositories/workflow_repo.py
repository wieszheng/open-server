"""工作流数据访问"""
from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Workflow, TestCase
from app.repositories.base import BaseRepository


class WorkflowRepository(BaseRepository[Workflow]):
    """工作流数据访问层"""

    def __init__(self, db: AsyncSession):
        """初始化工作流 Repository"""
        super().__init__(Workflow, db)

    async def get_by_test_case_id(self, test_case_id: int) -> Optional[Workflow]:
        """
        根据测试用例 ID 获取工作流。

        Args:
            test_case_id: 测试用例 ID。

        Returns:
            工作流对象，如果不存在则返回 None。
        """
        result = await self.db.execute(
            select(Workflow).where(Workflow.test_case_id == test_case_id)
        )
        return result.scalar_one_or_none()

    async def get_workflow_with_case(self, workflow_id: int) -> Optional[Workflow]:
        """
        获取工作流及其关联的测试用例。

        Args:
            workflow_id: 工作流 ID。

        Returns:
            工作流对象，如果不存在则返回 None。
        """
        result = await self.db.execute(
            select(Workflow)
            .options(selectinload(Workflow.test_case))
            .where(Workflow.id == workflow_id)
        )
        return result.scalar_one_or_none()

    async def get_all_workflows(
        self, skip: int = 0, limit: int = 100
    ) -> List[Workflow]:
        """
        获取工作流列表。

        Args:
            skip: 跳过的记录数。
            limit: 返回的最大记录数。

        Returns:
            工作流列表。
        """
        result = await self.db.execute(
            select(Workflow)
            .options(selectinload(Workflow.test_case))
            .offset(skip)
            .limit(limit)
            .order_by(Workflow.updated_at.desc())
        )
        return list(result.scalars().all())

    async def get_workflowed_test_case_ids(self) -> List[int]:
        """
        获取已有工作流的所有测试用例 ID。

        Returns:
            测试用例 ID 列表。
        """
        result = await self.db.execute(select(Workflow.test_case_id))
        return [row[0] for row in result.fetchall()]

    async def upsert_flow(
        self, test_case_id: int, nodes: list, edges: list
    ) -> Workflow:
        """
        保存工作流（upsert）：不存在则创建，存在则更新。

        Args:
            test_case_id: 测试用例 ID。
            nodes: 节点列表。
            edges: 边列表。

        Returns:
            创建或更新后的工作流。
        """
        existing = await self.get_by_test_case_id(test_case_id)

        # 同步：有 flow 即视为已自动化
        result = await self.db.execute(
            select(TestCase).where(TestCase.id == test_case_id)
        )
        test_case = result.scalar_one_or_none()
        if test_case:
            test_case.is_automated = True

        if existing:
            existing.nodes = nodes
            existing.edges = edges
            existing.updated_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(existing)
            return existing

        workflow = Workflow(
            test_case_id=test_case_id,
            nodes=nodes,
            edges=edges,
        )
        self.db.add(workflow)
        await self.db.commit()
        await self.db.refresh(workflow)
        return workflow

    async def delete_with_test_case_sync(self, workflow_id: int) -> bool:
        """
        删除工作流，同步取消测试用例的自动化标记。

        Args:
            workflow_id: 工作流 ID。

        Returns:
            是否删除成功。
        """
        workflow = await self.get_by_id(workflow_id)
        if not workflow:
            return False

        test_case_id = workflow.test_case_id
        await self.db.delete(workflow)

        result = await self.db.execute(
            select(TestCase).where(TestCase.id == test_case_id)
        )
        test_case = result.scalar_one_or_none()
        if test_case:
            test_case.is_automated = False

        await self.db.commit()
        return True
