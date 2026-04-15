"""测试执行数据访问"""
from typing import List
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TestExecution
from app.repositories.base import BaseRepository


class TestExecutionRepository(BaseRepository[TestExecution]):
    """测试执行数据访问层"""

    def __init__(self, db: AsyncSession):
        """初始化测试执行 Repository"""
        super().__init__(TestExecution, db)

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
        result = await self.db.execute(
            select(TestExecution)
            .order_by(TestExecution.timestamp.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_console_stats(self, days: int = 7) -> dict:
        """
        获取控制台统计数据（最近 N 天）。

        Args:
            days: 统计天数。

        Returns:
            包含统计数据的字典。
        """
        since = datetime.now(timezone.utc) - timedelta(days=days)

        result = await self.db.execute(
            select(TestExecution)
            .where(TestExecution.timestamp >= since)
            .order_by(TestExecution.timestamp.desc())
        )
        executions = list(result.scalars().all())

        if not executions:
            return {
                "total_tests": 0,
                "total_cases": 0,
                "passed_cases": 0,
                "failed_cases": 0,
                "avg_duration": 0.0,
                "trend": [],
            }

        total_tests = len(executions)
        total_cases = sum(e.total_cases for e in executions)
        passed_cases = sum(e.passed_cases for e in executions)
        failed_cases = sum(e.failed_cases for e in executions)
        avg_duration = sum(e.duration for e in executions) / total_tests

        # 计算每日趋势
        daily_data = {}
        for e in executions:
            date_str = e.timestamp.strftime("%Y-%m-%d")
            if date_str not in daily_data:
                daily_data[date_str] = []
            daily_data[date_str].append(e.duration)

        trend = []
        for date_str in sorted(daily_data.keys(), reverse=True)[:days]:
            durations = daily_data[date_str]
            trend.append(
                {
                    "date": date_str,
                    "avg_duration": round(sum(durations) / len(durations), 2),
                    "min_duration": round(min(durations), 2),
                    "max_duration": round(max(durations), 2),
                    "total_executions": len(durations),
                }
            )

        return {
            "total_tests": total_tests,
            "total_cases": total_cases,
            "passed_cases": passed_cases,
            "failed_cases": failed_cases,
            "avg_duration": round(avg_duration, 2),
            "trend": trend,
        }
