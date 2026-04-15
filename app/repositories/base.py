"""通用数据访问基类"""
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    通用数据访问基类。

    提供基础的 CRUD 操作，所有具体的 Repository 都应继承此类。
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        初始化 Repository。

        Args:
            model: SQLAlchemy 模型类。
            db: 异步数据库会话。
        """
        self.model = model
        self.db = db

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        根据 ID 获取单个对象。

        Args:
            id: 对象 ID。

        Returns:
            找到的对象，如果不存在则返回 None。
        """
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        获取所有对象列表。

        Args:
            skip: 跳过的记录数。
            limit: 返回的最大记录数。

        Returns:
            对象列表。
        """
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, **kwargs) -> ModelType:
        """
        创建新对象。

        Args:
            **kwargs: 对象属性。

        Returns:
            创建的对象。
        """
        db_obj = self.model(**kwargs)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: ModelType, **kwargs) -> ModelType:
        """
        更新对象。

        Args:
            db_obj: 要更新的对象。
            **kwargs: 要更新的属性。

        Returns:
            更新后的对象。
        """
        for key, value in kwargs.items():
            setattr(db_obj, key, value)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: ModelType) -> bool:
        """
        删除对象。

        Args:
            db_obj: 要删除的对象。

        Returns:
            是否删除成功。
        """
        await self.db.delete(db_obj)
        await self.db.commit()
        return True

    async def count(self) -> int:
        """
        获取对象总数。

        Returns:
            对象总数。
        """
        result = await self.db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar() or 0
