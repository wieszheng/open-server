"""测试用例业务逻辑"""
from typing import List, Optional
from datetime import datetime, timezone

from app.models import TestCase
from app.repositories import TestCaseRepository, DirectoryRepository
from app.schemas import TestCaseCreate, TestCaseUpdate


class TestCaseService:
    """测试用例业务逻辑层"""

    def __init__(self, repo: TestCaseRepository, dir_repo: DirectoryRepository):
        """
        初始化测试用例服务。

        Args:
            repo: 测试用例数据访问对象。
            dir_repo: 目录数据访问对象。
        """
        self.repo = repo
        self.dir_repo = dir_repo

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
        获取测试用例列表。

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
        return await self.repo.get_test_cases(
            skip=skip,
            limit=limit,
            case_type=case_type,
            priority=priority,
            status=status,
            module=module,
            search=search,
        )

    async def get_test_case(self, case_id: int) -> Optional[TestCase]:
        """
        获取单个测试用例。

        Args:
            case_id: 测试用例 ID。

        Returns:
            测试用例对象，如果不存在则返回 None。
        """
        return await self.repo.get_by_id(case_id)

    async def get_test_case_stats(self) -> dict:
        """
        获取测试用例统计信息。

        Returns:
            包含统计数据的字典。
        """
        return await self.repo.get_stats()

    async def create_test_case(self, case_data: TestCaseCreate) -> TestCase:
        """
        创建测试用例。

        Args:
            case_data: 测试用例创建数据。

        Returns:
            创建的测试用例对象。
        """
        data = case_data.model_dump()
        # 将 tags 列表转换为逗号分隔的字符串
        data["tags"] = ",".join(data.get("tags", []))
        db_case = await self.repo.create(**data)

        # 更新目录用例数量
        if db_case.directory_id:
            await self.dir_repo.update_case_count(db_case.directory_id)

        return db_case

    async def update_test_case(
        self, case_id: int, case_data: TestCaseUpdate
    ) -> Optional[TestCase]:
        """
        更新测试用例。

        Args:
            case_id: 测试用例 ID。
            case_data: 测试用例更新数据。

        Returns:
            更新后的测试用例对象，如果不存在则返回 None。
        """
        db_case = await self.repo.get_by_id(case_id)
        if not db_case:
            return None

        old_directory_id = db_case.directory_id
        update_data = case_data.model_dump(exclude_unset=True)

        # 将 tags 列表转换为逗号分隔的字符串
        if "tags" in update_data:
            update_data["tags"] = ",".join(update_data["tags"])

        update_data["updated_at"] = datetime.now(timezone.utc)
        db_case = await self.repo.update(db_case, **update_data)

        # 目录变更时同步更新新旧目录的计数
        new_directory_id = db_case.directory_id
        if old_directory_id != new_directory_id:
            if old_directory_id:
                await self.dir_repo.update_case_count(old_directory_id)
            if new_directory_id:
                await self.dir_repo.update_case_count(new_directory_id)

        return db_case

    async def delete_test_case(self, case_id: int) -> bool:
        """
        删除测试用例。

        Args:
            case_id: 测试用例 ID。

        Returns:
            是否删除成功。
        """
        db_case = await self.repo.get_by_id(case_id)
        if not db_case:
            return False

        directory_id = db_case.directory_id
        success = await self.repo.delete(db_case)

        # 更新目录用例数量
        if directory_id and success:
            await self.dir_repo.update_case_count(directory_id)

        return success
