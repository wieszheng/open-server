"""脚本数据访问"""
from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Script
from app.repositories.base import BaseRepository


class ScriptRepository(BaseRepository[Script]):
    """脚本数据访问层"""

    def __init__(self, db: AsyncSession):
        """初始化脚本 Repository"""
        super().__init__(Script, db)

    async def get_scripts(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Script]:
        """
        获取脚本列表，支持筛选和搜索。

        Args:
            skip: 跳过的记录数。
            limit: 返回的最大记录数。
            category: 按分类筛选。
            search: 按名称或描述搜索。

        Returns:
            脚本列表。
        """
        query = select(Script)

        if category and category != "all":
            query = query.where(Script.category == category)

        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                (Script.name.ilike(search_pattern))
                | (Script.description.ilike(search_pattern))
            )

        query = query.order_by(Script.updated_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_featured(self, limit: int = 4) -> List[Script]:
        """
        获取精选脚本。

        Args:
            limit: 返回的最大记录数。

        Returns:
            精选脚本列表。
        """
        result = await self.db.execute(
            select(Script)
            .where(Script.featured == True)
            .order_by(Script.rating.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def increment_views(self, script_id: int) -> Optional[Script]:
        """
        增加脚本浏览量。

        Args:
            script_id: 脚本 ID。

        Returns:
            更新后的脚本，如果不存在则返回 None。
        """
        db_script = await self.get_by_id(script_id)
        if not db_script:
            return None

        db_script.views += 1
        await self.db.commit()
        await self.db.refresh(db_script)
        return db_script

    async def increment_downloads(self, script_id: int) -> Optional[Script]:
        """
        增加脚本下载量。

        Args:
            script_id: 脚本 ID。

        Returns:
            更新后的脚本，如果不存在则返回 None。
        """
        db_script = await self.get_by_id(script_id)
        if not db_script:
            return None

        db_script.downloads += 1
        await self.db.commit()
        await self.db.refresh(db_script)
        return db_script
