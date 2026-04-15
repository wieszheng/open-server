"""数据库连接和会话管理"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# 创建异步会话工厂
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类"""

    pass


async def get_db() -> AsyncSession:
    """
    获取数据库会话。

    Yields:
        AsyncSession: 异步数据库会话对象。
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    初始化数据库，创建所有表。
    """
    # 导入所有模型以确保它们被注册
    from app.models import Script, TestCase, TestExecution, Directory, Workflow  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
