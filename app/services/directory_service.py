"""目录业务逻辑"""
from typing import List, Optional
from datetime import datetime, timezone

from app.models import Directory, TestCase
from app.repositories import DirectoryRepository
from app.schemas import DirectoryCreate, DirectoryUpdate


class DirectoryService:
    """目录业务逻辑层"""

    def __init__(self, repo: DirectoryRepository):
        """
        初始化目录服务。

        Args:
            repo: 目录数据访问对象。
        """
        self.repo = repo

    async def get_directories(self) -> List[Directory]:
        """
        获取所有根目录列表（包含子目录）。

        Returns:
            根目录列表。
        """
        return await self.repo.get_all_directories()

    async def get_directory(self, directory_id: int) -> Optional[Directory]:
        """
        获取单个目录及其子目录。

        Args:
            directory_id: 目录 ID。

        Returns:
            目录对象，如果不存在则返回 None。
        """
        return await self.repo.get_directory_with_children(directory_id)

    async def get_children(self, parent_id: int) -> List[Directory]:
        """
        获取指定父目录的所有子目录。

        Args:
            parent_id: 父目录 ID。

        Returns:
            子目录列表。
        """
        return await self.repo.get_children(parent_id)

    async def create_directory(self, dir_data: DirectoryCreate) -> Directory:
        """
        创建目录。

        Args:
            dir_data: 目录创建数据。

        Returns:
            创建的目录对象。
        """
        db_dir = await self.repo.create(**dir_data.model_dump())
        # 更新用例数量统计
        await self.repo.update_case_count(db_dir.id)
        return db_dir

    async def update_directory(
        self, directory_id: int, dir_data: DirectoryUpdate
    ) -> Optional[Directory]:
        """
        更新目录。

        Args:
            directory_id: 目录 ID。
            dir_data: 目录更新数据。

        Returns:
            更新后的目录对象，如果不存在则返回 None。
        """
        db_dir = await self.repo.get_by_id(directory_id)
        if not db_dir:
            return None

        update_data = dir_data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now(timezone.utc)
        return await self.repo.update(db_dir, **update_data)

    async def delete_directory(self, directory_id: int) -> bool:
        """
        删除目录及其所有子目录，将用例移至无目录。

        Args:
            directory_id: 目录 ID。

        Returns:
            是否删除成功。
        """
        db_dir = await self.repo.get_by_id(directory_id)
        if not db_dir:
            return False

        return await self.repo.delete_with_children(directory_id)
