"""添加 parent_id 字段到 directories 表"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.database import engine


async def add_parent_id_column():
    """添加 parent_id 列"""
    async with engine.begin() as conn:
        # 检查列是否已存在
        result = await conn.execute(
            text("PRAGMA table_info(directories)")
        )
        columns = [row[1] for row in result.fetchall()]

        if "parent_id" not in columns:
            print("Adding parent_id column to directories table...")
            await conn.execute(
                text(
                    "ALTER TABLE directories ADD COLUMN parent_id INTEGER REFERENCES directories(id)"
                )
            )
            print("✓ parent_id column added successfully")
        else:
            print("✓ parent_id column already exists")


if __name__ == "__main__":
    asyncio.run(add_parent_id_column())
