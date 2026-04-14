"""初始化脚本示例数据"""
import asyncio
from datetime import datetime, timedelta
import random

from database import async_session_maker, init_db
from models import Script, TestExecution


async def seed_scripts():
    """填充脚本示例数据"""
    await init_db()
    
    async with async_session_maker() as session:
        from sqlalchemy import select
        result = await session.execute(select(Script))
        existing = result.scalars().first()
        if existing:
            print("脚本数据已存在，跳过初始化")
            return
        
        scripts = [
            Script(
                name="API 自动化测试脚本",
                description="基于 REST Assured 的 API 自动化测试框架，支持参数化配置",
                code="import pytest\n\ndef test_api_demo():\n    assert True",
                category="api",
                author="张三",
                tags=["API", "自动化", "REST"],
                rating=4.8,
                downloads=156,
                views=523,
                featured=True,
            ),
            Script(
                name="UI 回归测试脚本",
                description="Playwright 驱动的 UI 回归测试脚本",
                code="from playwright.sync_api import sync_playwright",
                category="ui",
                author="李四",
                tags=["UI", "Playwright", "回归测试"],
                rating=4.5,
                downloads=89,
                views=234,
                featured=True,
            ),
            Script(
                name="性能测试脚本",
                description="Locust 性能测试脚本，支持分布式压测",
                code="from locust import HttpUser, task",
                category="performance",
                author="王五",
                tags=["性能", "Locust", "压测"],
                rating=4.2,
                downloads=67,
                views=189,
                featured=False,
            ),
            Script(
                name="数据验证脚本",
                description="数据质量和一致性验证脚本",
                code="# 数据验证脚本",
                category="data",
                author="赵六",
                tags=["数据", "验证", "质量"],
                rating=4.0,
                downloads=45,
                views=123,
                featured=False,
            ),
            Script(
                name="安全扫描脚本",
                description="OWASP ZAP 安全扫描集成脚本",
                code="# 安全扫描脚本",
                category="security",
                author="孙七",
                tags=["安全", "OWASP", "扫描"],
                rating=4.6,
                downloads=78,
                views=201,
                featured=True,
            ),
        ]
        
        session.add_all(scripts)
        
        # 测试执行记录示例数据
        now = datetime.utcnow()
        executions = []
        for i in range(50):
            executions.append(TestExecution(
                timestamp=now - timedelta(hours=i * 2),
                duration=round(random.uniform(5.0, 120.0), 2),
                total_cases=random.randint(50, 500),
                passed_cases=random.randint(40, 480),
                failed_cases=random.randint(0, 20),
                environment="production" if i % 3 == 0 else "staging",
            ))
        
        session.add_all(executions)
        await session.commit()
        print("脚本示例数据初始化完成")


if __name__ == "__main__":
    asyncio.run(seed_scripts())
