"""初始化目录示例数据"""
import asyncio

from database import async_session_maker, init_db
from models_directory import Directory


async def seed_directories():
    """填充目录示例数据"""
    await init_db()

    async with async_session_maker() as session:
        from sqlalchemy import select
        result = await session.execute(select(Directory))
        existing = result.scalars().first()
        if existing:
            print("目录数据已存在，跳过初始化")
            return

        directories = [
            Directory(
                name="用户中心",
                description="用户相关的微服务",
                icon="users",
                color="blue",
                sort_order=1,
            ),
            Directory(
                name="商品服务",
                description="商品相关的微服务",
                icon="package",
                color="green",
                sort_order=2,
            ),
            Directory(
                name="订单服务",
                description="订单相关的微服务",
                icon="shopping-cart",
                color="orange",
                sort_order=3,
            ),
            Directory(
                name="通知服务",
                description="通知相关的微服务",
                icon="bell",
                color="purple",
                sort_order=4,
            ),
            Directory(
                name="报表服务",
                description="报表相关的微服务",
                icon="bar-chart",
                color="red",
                sort_order=5,
            ),
        ]

        session.add_all(directories)
        await session.commit()
        print("目录示例数据初始化完成")


if __name__ == "__main__":
    asyncio.run(seed_directories())
