"""更新所有目录的用例数量统计"""
import asyncio

from database import async_session_maker, init_db
from models_directory import Directory
from models_test_case import TestCase
from sqlalchemy import select, func


async def update_all_directory_case_counts():
    """更新所有目录的用例数量"""
    await init_db()

    async with async_session_maker() as session:
        # 获取所有目录
        result = await session.execute(select(Directory))
        directories = result.scalars().all()

        if not directories:
            print("没有找到目录")
            return

        for directory in directories:
            # 统计该目录下的用例数量
            count_result = await session.execute(
                select(func.count()).select_from(TestCase).where(
                    TestCase.directory_id == directory.id
                )
            )
            count = count_result.scalar() or 0
            directory.case_count = count
            print(f"目录 '{directory.name}' (ID={directory.id}): {count} 个用例")

        await session.commit()
        print("目录用例数量更新完成")


if __name__ == "__main__":
    asyncio.run(update_all_directory_case_counts())
