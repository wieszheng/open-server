"""数据库连接和会话管理"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    """获取数据库会话"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """初始化数据库"""
    # 导入所有模型以确保它们被注册
    from models import Script, TestExecution  # noqa
    from models_test_case import TestCase  # noqa
    from models_directory import Directory  # noqa
    from models_workflow import Workflow  # noqa

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
