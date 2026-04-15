"""Pytest 配置和 fixtures"""
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.main import app
from app.database import get_async_session, Base
from app.config import settings

# 测试数据库 URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_scripts.db"

# 创建测试引擎
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """覆盖数据库依赖，使用测试数据库"""
    async with test_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


# 覆盖依赖
app.dependency_overrides[get_async_session] = override_get_db


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    提供独立的数据库会话用于每个测试。

    Yields:
        AsyncSession: 测试数据库会话。
    """
    async with test_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    提供 HTTP 客户端用于测试 API 端点。

    Yields:
        AsyncClient: 异步 HTTP 客户端。
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """在所有测试开始前创建数据库表"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
