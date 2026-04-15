"""控制台业务逻辑"""
from typing import List

from app.models import TestExecution
from app.repositories import TestExecutionRepository
from app.schemas import TestExecutionCreate


class ConsoleService:
    """控制台业务逻辑层"""

    def __init__(self, repo: TestExecutionRepository):
        """
        初始化控制台服务。

        Args:
            repo: 测试执行数据访问对象。
        """
        self.repo = repo

    async def get_console_stats(self, days: int = 7) -> dict:
        """
        获取控制台统计数据。

        Args:
            days: 统计天数。

        Returns:
            包含统计数据的字典。
        """
        return await self.repo.get_console_stats(days=days)

    async def get_executions(
        self, skip: int = 0, limit: int = 100
    ) -> List[TestExecution]:
        """
        获取测试执行记录列表。

        Args:
            skip: 跳过的记录数。
            limit: 返回的最大记录数。

        Returns:
            测试执行记录列表。
        """
        return await self.repo.get_executions(skip=skip, limit=limit)

    async def create_execution(
        self, execution_data: TestExecutionCreate
    ) -> TestExecution:
        """
        创建测试执行记录。

        Args:
            execution_data: 测试执行创建数据。

        Returns:
            创建的测试执行对象。
        """
        return await self.repo.create(**execution_data.model_dump())
