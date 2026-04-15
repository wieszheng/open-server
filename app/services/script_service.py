"""脚本业务逻辑"""
from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Script
from app.repositories import ScriptRepository
from app.schemas import ScriptCreate, ScriptUpdate


class ScriptService:
    """脚本业务逻辑层"""

    def __init__(self, repo: ScriptRepository):
        """
        初始化脚本服务。

        Args:
            repo: 脚本数据访问对象。
        """
        self.repo = repo

    async def get_scripts(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Script]:
        """
        获取脚本列表。

        Args:
            skip: 跳过的记录数。
            limit: 返回的最大记录数。
            category: 按分类筛选。
            search: 按名称或描述搜索。

        Returns:
            脚本列表。
        """
        return await self.repo.get_scripts(
            skip=skip, limit=limit, category=category, search=search
        )

    async def get_script(self, script_id: int) -> Optional[Script]:
        """
        获取单个脚本。

        Args:
            script_id: 脚本 ID。

        Returns:
            脚本对象，如果不存在则返回 None。
        """
        return await self.repo.get_by_id(script_id)

    async def get_featured_scripts(self, limit: int = 4) -> List[Script]:
        """
        获取精选脚本。

        Args:
            limit: 返回的最大记录数。

        Returns:
            精选脚本列表。
        """
        return await self.repo.get_featured(limit=limit)

    async def create_script(self, script_data: ScriptCreate) -> Script:
        """
        创建新脚本。

        Args:
            script_data: 脚本创建数据。

        Returns:
            创建的脚本对象。
        """
        return await self.repo.create(**script_data.model_dump())

    async def update_script(
        self, script_id: int, script_data: ScriptUpdate
    ) -> Optional[Script]:
        """
        更新脚本。

        Args:
            script_id: 脚本 ID。
            script_data: 脚本更新数据。

        Returns:
            更新后的脚本对象，如果不存在则返回 None。
        """
        db_script = await self.repo.get_by_id(script_id)
        if not db_script:
            return None

        update_data = script_data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now(timezone.utc)
        return await self.repo.update(db_script, **update_data)

    async def delete_script(self, script_id: int) -> bool:
        """
        删除脚本。

        Args:
            script_id: 脚本 ID。

        Returns:
            是否删除成功。
        """
        db_script = await self.repo.get_by_id(script_id)
        if not db_script:
            return False
        return await self.repo.delete(db_script)

    async def increment_views(self, script_id: int) -> Optional[Script]:
        """
        增加脚本浏览量。

        Args:
            script_id: 脚本 ID。

        Returns:
            更新后的脚本，如果不存在则返回 None。
        """
        return await self.repo.increment_views(script_id)

    async def increment_downloads(self, script_id: int) -> Optional[Script]:
        """
        增加脚本下载量。

        Args:
            script_id: 脚本 ID。

        Returns:
            更新后的脚本，如果不存在则返回 None。
        """
        return await self.repo.increment_downloads(script_id)
