"""工作流业务逻辑"""
from typing import List, Optional

from app.models import Workflow
from app.repositories import WorkflowRepository
from app.schemas import FlowUpsert, WorkflowUpdate


class WorkflowService:
    """工作流业务逻辑层"""

    def __init__(self, repo: WorkflowRepository):
        """
        初始化工作流服务。

        Args:
            repo: 工作流数据访问对象。
        """
        self.repo = repo

    async def get_workflows(
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
        return await self.repo.get_all_workflows(skip=skip, limit=limit)

    async def get_workflow(self, workflow_id: int) -> Optional[Workflow]:
        """
        获取工作流详情。

        Args:
            workflow_id: 工作流 ID。

        Returns:
            工作流对象，如果不存在则返回 None。
        """
        return await self.repo.get_workflow_with_case(workflow_id)

    async def get_workflow_by_test_case(
        self, test_case_id: int
    ) -> Optional[Workflow]:
        """
        根据测试用例 ID 获取工作流。

        Args:
            test_case_id: 测试用例 ID。

        Returns:
            工作流对象，如果不存在则返回 None。
        """
        return await self.repo.get_by_test_case_id(test_case_id)

    async def get_workflowed_test_case_ids(self) -> List[int]:
        """
        获取已有工作流的所有测试用例 ID。

        Returns:
            测试用例 ID 列表。
        """
        return await self.repo.get_workflowed_test_case_ids()

    async def upsert_flow(
        self, test_case_id: int, flow_data: FlowUpsert
    ) -> Workflow:
        """
        保存工作流（不存在则创建，存在则更新）。

        Args:
            test_case_id: 测试用例 ID。
            flow_data: 工作流数据。

        Returns:
            创建或更新后的工作流对象。
        """
        return await self.repo.upsert_flow(
            test_case_id=test_case_id,
            nodes=flow_data.nodes,
            edges=flow_data.edges,
        )

    async def update_workflow(
        self, workflow_id: int, workflow_data: WorkflowUpdate
    ) -> Optional[Workflow]:
        """
        更新工作流。

        Args:
            workflow_id: 工作流 ID。
            workflow_data: 工作流更新数据。

        Returns:
            更新后的工作流对象，如果不存在则返回 None。
        """
        db_workflow = await self.repo.get_by_id(workflow_id)
        if not db_workflow:
            return None

        update_data = workflow_data.model_dump(exclude_unset=True)
        return await self.repo.update(db_workflow, **update_data)

    async def delete_workflow(self, workflow_id: int) -> bool:
        """
        删除工作流，同步取消测试用例的自动化标记。

        Args:
            workflow_id: 工作流 ID。

        Returns:
            是否删除成功。
        """
        return await self.repo.delete_with_test_case_sync(workflow_id)
