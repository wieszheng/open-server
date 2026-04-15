"""测试用例数据访问"""
from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TestCase
from app.repositories.base import BaseRepository


class TestCaseRepository(BaseRepository[TestCase]):
    """测试用例数据访问层"""

    def __init__(self, db: AsyncSession):
        """初始化测试用例 Repository"""
        super().__init__(TestCase, db)

    async def get_test_cases(
        self,
        skip: int = 0,
        limit: int = 100,
        case_type: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        module: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[TestCase]:
        """
        获取测试用例列表，支持筛选和搜索。

        Args:
            skip: 跳过的记录数。
            limit: 返回的最大记录数。
            case_type: 按用例类型筛选。
            priority: 按优先级筛选。
            status: 按状态筛选。
            module: 按模块筛选。
            search: 按名称或描述搜索。

        Returns:
            测试用例列表。
        """
        query = select(TestCase)

        if case_type and case_type != "all":
            query = query.where(TestCase.case_type == case_type)

        if priority and priority != "all":
            query = query.where(TestCase.priority == priority)

        if status and status != "all":
            query = query.where(TestCase.status == status)

        if module and module != "all":
            query = query.where(TestCase.module == module)

        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                (TestCase.name.ilike(search_pattern))
                | (TestCase.description.ilike(search_pattern))
            )

        query = query.order_by(TestCase.updated_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_module(self, module: str) -> List[TestCase]:
        """
        按模块获取测试用例。

        Args:
            module: 模块名称。

        Returns:
            测试用例列表。
        """
        result = await self.db.execute(
            select(TestCase)
            .where(TestCase.module == module)
            .order_by(TestCase.priority.asc(), TestCase.name)
        )
        return list(result.scalars().all())

    async def get_stats(self) -> dict:
        """
        获取测试用例统计信息。

        Returns:
            包含统计数据的字典。
        """
        result = await self.db.execute(select(TestCase))
        cases = list(result.scalars().all())

        total = len(cases)
        automated = sum(1 for c in cases if c.is_automated)
        flaky = sum(1 for c in cases if c.flaky)

        by_type = {}
        by_priority = {}
        by_status = {}
        by_module = {}

        for c in cases:
            by_type[c.case_type] = by_type.get(c.case_type, 0) + 1
            by_priority[c.priority] = by_priority.get(c.priority, 0) + 1
            by_status[c.status] = by_status.get(c.status, 0) + 1
            if c.module:
                by_module[c.module] = by_module.get(c.module, 0) + 1

        return {
            "total": total,
            "automated": automated,
            "manual": total - automated,
            "flaky": flaky,
            "pass_rate": round(
                sum(c.passed_runs for c in cases)
                / max(sum(c.total_runs for c in cases), 1)
                * 100,
                1,
            ),
            "by_type": by_type,
            "by_priority": by_priority,
            "by_status": by_status,
            "by_module": by_module,
        }
