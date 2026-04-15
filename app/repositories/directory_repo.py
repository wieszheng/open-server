"""目录数据访问"""
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Directory, TestCase
from app.repositories.base import BaseRepository


class DirectoryRepository(BaseRepository[Directory]):
    """目录数据访问层"""

    def __init__(self, db: AsyncSession):
        """初始化目录 Repository"""
        super().__init__(Directory, db)

    async def get_all_directories(self) -> List[Directory]:
        """
        获取所有目录（扁平列表），按排序顺序排列。

        Returns:
            目录列表（扁平结构）。
        """
        result = await self.db.execute(
            select(Directory)
            .order_by(Directory.sort_order.asc(), Directory.name)
        )
        return list(result.scalars().all())

    async def get_directory_with_children(self, directory_id: int) -> Optional[Directory]:
        """
        获取目录及其子目录。

        Args:
            directory_id: 目录 ID。

        Returns:
            目录对象，如果不存在则返回 None。
        """
        result = await self.db.execute(
            select(Directory)
            .options(selectinload(Directory.children))
            .where(Directory.id == directory_id)
        )
        return result.scalar_one_or_none()

    async def get_children(self, parent_id: int) -> List[Directory]:
        """
        获取指定父目录的所有子目录。

        Args:
            parent_id: 父目录 ID。

        Returns:
            子目录列表。
        """
        result = await self.db.execute(
            select(Directory)
            .where(Directory.parent_id == parent_id)
            .order_by(Directory.sort_order.asc(), Directory.name)
        )
        return list(result.scalars().all())

    async def update_case_count(self, directory_id: int) -> None:
        """
        更新目录的用例数量。

        Args:
            directory_id: 目录 ID。
        """
        db_dir = await self.get_by_id(directory_id)
        if not db_dir:
            return

        result = await self.db.execute(
            select(func.count())
            .select_from(TestCase)
            .where(TestCase.directory_id == directory_id)
        )
        count = result.scalar() or 0
        db_dir.case_count = count
        await self.db.commit()

    async def delete_with_children(
        self, directory_id: int, move_cases_to_null: bool = True
    ) -> bool:
        """
        删除目录及其所有子目录。

        Args:
            directory_id: 目录 ID。
            move_cases_to_null: 是否将用例移至无目录。

        Returns:
            是否删除成功。
        """
        # 递归获取所有子目录
        all_dirs_to_delete = []
        queue = [directory_id]

        while queue:
            current_id = queue.pop(0)
            all_dirs_to_delete.append(current_id)
            children = await self.get_children(current_id)
            for child in children:
                queue.append(child.id)

        # 将所有子目录下的用例移至无目录
        if move_cases_to_null:
            for dir_id in all_dirs_to_delete:
                result = await self.db.execute(
                    select(TestCase).where(TestCase.directory_id == dir_id)
                )
                cases = result.scalars().all()
                for case in cases:
                    case.directory_id = None

        # 删除所有目录
        for dir_id in all_dirs_to_delete:
            db_dir = await self.get_by_id(dir_id)
            if db_dir:
                await self.db.delete(db_dir)

        await self.db.commit()
        return True
