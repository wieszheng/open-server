"""依赖注入"""
from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, async_session_maker
from app.repositories import (
    ScriptRepository,
    TestCaseRepository,
    DirectoryRepository,
    WorkflowRepository,
)
from app.repositories.console_repo import TestExecutionRepository
from app.services import (
    ScriptService,
    TestCaseService,
    DirectoryService,
    WorkflowService,
    ConsoleService,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取异步数据库会话。

    Yields:
        AsyncSession: 异步数据库会话对象。
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


# ==================== Repository 依赖 ====================


def get_script_repo(
    db: AsyncSession = Depends(get_async_session),
) -> ScriptRepository:
    """
    获取脚本 Repository。

    Args:
        db: 异步数据库会话。

    Returns:
        ScriptRepository: 脚本数据访问对象。
    """
    return ScriptRepository(db)


def get_test_case_repo(
    db: AsyncSession = Depends(get_async_session),
) -> TestCaseRepository:
    """
    获取测试用例 Repository。

    Args:
        db: 异步数据库会话。

    Returns:
        TestCaseRepository: 测试用例数据访问对象。
    """
    return TestCaseRepository(db)


def get_directory_repo(
    db: AsyncSession = Depends(get_async_session),
) -> DirectoryRepository:
    """
    获取目录 Repository。

    Args:
        db: 异步数据库会话。

    Returns:
        DirectoryRepository: 目录数据访问对象。
    """
    return DirectoryRepository(db)


def get_workflow_repo(
    db: AsyncSession = Depends(get_async_session),
) -> WorkflowRepository:
    """
    获取工作流 Repository。

    Args:
        db: 异步数据库会话。

    Returns:
        WorkflowRepository: 工作流数据访问对象。
    """
    return WorkflowRepository(db)


def get_test_execution_repo(
    db: AsyncSession = Depends(get_async_session),
) -> TestExecutionRepository:
    """
    获取测试执行 Repository。

    Args:
        db: 异步数据库会话。

    Returns:
        TestExecutionRepository: 测试执行数据访问对象。
    """
    return TestExecutionRepository(db)


# ==================== Service 依赖 ====================


def get_script_service(
    repo: ScriptRepository = Depends(get_script_repo),
) -> ScriptService:
    """
    获取脚本 Service。

    Args:
        repo: 脚本 Repository。

    Returns:
        ScriptService: 脚本业务逻辑对象。
    """
    return ScriptService(repo)


def get_test_case_service(
    test_case_repo: TestCaseRepository = Depends(get_test_case_repo),
    dir_repo: DirectoryRepository = Depends(get_directory_repo),
) -> TestCaseService:
    """
    获取测试用例 Service。

    Args:
        test_case_repo: 测试用例 Repository。
        dir_repo: 目录 Repository。

    Returns:
        TestCaseService: 测试用例业务逻辑对象。
    """
    return TestCaseService(test_case_repo, dir_repo)


def get_directory_service(
    repo: DirectoryRepository = Depends(get_directory_repo),
) -> DirectoryService:
    """
    获取目录 Service。

    Args:
        repo: 目录 Repository。

    Returns:
        DirectoryService: 目录业务逻辑对象。
    """
    return DirectoryService(repo)


def get_workflow_service(
    repo: WorkflowRepository = Depends(get_workflow_repo),
) -> WorkflowService:
    """
    获取工作流 Service。

    Args:
        repo: 工作流 Repository。

    Returns:
        WorkflowService: 工作流业务逻辑对象。
    """
    return WorkflowService(repo)


def get_console_service(
    repo: TestExecutionRepository = Depends(get_test_execution_repo),
) -> ConsoleService:
    """
    获取控制台 Service。

    Args:
        repo: 测试执行 Repository。

    Returns:
        ConsoleService: 控制台业务逻辑对象。
    """
    return ConsoleService(repo)
