"""CRUD 操作"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models import Script, TestExecution
from models_test_case import TestCase
from models_directory import Directory
from schemas import ScriptCreate, ScriptUpdate, TestExecutionCreate, TestCaseCreate, TestCaseUpdate, DirectoryCreate, DirectoryUpdate


# ===================== 脚本 CRUD =====================
async def get_scripts(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    search: Optional[str] = None,
) -> List[Script]:
    """获取脚本列表"""
    query = select(Script)
    
    if category and category != "all":
        query = query.where(Script.category == category)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (Script.name.ilike(search_pattern)) |
            (Script.description.ilike(search_pattern))
        )
    
    query = query.order_by(Script.updated_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_script(db: AsyncSession, script_id: int) -> Optional[Script]:
    """获取单个脚本"""
    result = await db.execute(select(Script).where(Script.id == script_id))
    return result.scalar_one_or_none()


async def get_featured_scripts(db: AsyncSession, limit: int = 4) -> List[Script]:
    """获取精选脚本"""
    result = await db.execute(
        select(Script)
        .where(Script.featured == True)
        .order_by(Script.rating.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_script(db: AsyncSession, script: ScriptCreate) -> Script:
    """创建脚本"""
    db_script = Script(**script.model_dump())
    db.add(db_script)
    await db.commit()
    await db.refresh(db_script)
    return db_script


async def update_script(
    db: AsyncSession, script_id: int, script: ScriptUpdate
) -> Optional[Script]:
    """更新脚本"""
    db_script = await get_script(db, script_id)
    if not db_script:
        return None
    
    update_data = script.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_script, key, value)
    
    db_script.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(db_script)
    return db_script


async def delete_script(db: AsyncSession, script_id: int) -> bool:
    """删除脚本"""
    db_script = await get_script(db, script_id)
    if not db_script:
        return False
    
    await db.delete(db_script)
    await db.commit()
    return True


async def increment_script_views(db: AsyncSession, script_id: int) -> Optional[Script]:
    """增加脚本浏览量"""
    db_script = await get_script(db, script_id)
    if not db_script:
        return None
    
    db_script.views += 1
    await db.commit()
    await db.refresh(db_script)
    return db_script


async def increment_script_downloads(db: AsyncSession, script_id: int) -> Optional[Script]:
    """增加脚本下载量"""
    db_script = await get_script(db, script_id)
    if not db_script:
        return None
    
    db_script.downloads += 1
    await db.commit()
    await db.refresh(db_script)
    return db_script


# ===================== 测试执行 CRUD =====================
async def get_test_executions(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    days: int = 30,
) -> List[TestExecution]:
    """获取测试执行记录"""
    result = await db.execute(
        select(TestExecution)
        .order_by(TestExecution.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_test_execution(
    db: AsyncSession, execution: TestExecutionCreate
) -> TestExecution:
    """创建测试执行记录"""
    db_execution = TestExecution(**execution.model_dump())
    db.add(db_execution)
    await db.commit()
    await db.refresh(db_execution)
    return db_execution


async def get_console_stats(db: AsyncSession, days: int = 7) -> dict:
    """获取控制台统计数据（最近 N 天）"""
    from datetime import timedelta
    since = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(TestExecution)
        .where(TestExecution.timestamp >= since)
        .order_by(TestExecution.timestamp.desc())
    )
    executions = list(result.scalars().all())
    
    if not executions:
        return {
            "total_tests": 0,
            "total_cases": 0,
            "passed_cases": 0,
            "failed_cases": 0,
            "avg_duration": 0.0,
            "trend": [],
        }
    
    total_tests = len(executions)
    total_cases = sum(e.total_cases for e in executions)
    passed_cases = sum(e.passed_cases for e in executions)
    failed_cases = sum(e.failed_cases for e in executions)
    avg_duration = sum(e.duration for e in executions) / total_tests
    
    # 计算每日趋势
    daily_data = {}
    for e in executions:
        date_str = e.timestamp.strftime("%Y-%m-%d")
        if date_str not in daily_data:
            daily_data[date_str] = []
        daily_data[date_str].append(e.duration)
    
    trend = []
    for date_str in sorted(daily_data.keys(), reverse=True)[:days]:
        durations = daily_data[date_str]
        trend.append({
            "date": date_str,
            "avg_duration": round(sum(durations) / len(durations), 2),
            "min_duration": round(min(durations), 2),
            "max_duration": round(max(durations), 2),
            "total_executions": len(durations),
        })
    
    return {
        "total_tests": total_tests,
        "total_cases": total_cases,
        "passed_cases": passed_cases,
        "failed_cases": failed_cases,
        "avg_duration": round(avg_duration, 2),
        "trend": trend,
    }


# ===================== 测试用例 CRUD =====================

async def get_test_cases(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    case_type: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    module: Optional[str] = None,
    search: Optional[str] = None,
) -> List[TestCase]:
    """获取测试用例列表"""
    query = select(TestCase)

    if case_type and case_type != "all":
        query = query.where(TestCase.case_type == case_type)

    if priority and priority != "all":
        query = query.where(TestCase.priority == priority)

    if status and status != "all":
        query = query.where(TestCase.status == status)

    if module and module != "all":
        query = query.where(TestCase.module == module)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (TestCase.name.ilike(search_pattern)) |
            (TestCase.description.ilike(search_pattern))
        )

    query = query.order_by(TestCase.updated_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_test_case(db: AsyncSession, case_id: int) -> Optional[TestCase]:
    """获取单个测试用例"""
    result = await db.execute(select(TestCase).where(TestCase.id == case_id))
    return result.scalar_one_or_none()


async def get_test_case_by_module(db: AsyncSession, module: str) -> List[TestCase]:
    """按模块获取测试用例"""
    result = await db.execute(
        select(TestCase)
        .where(TestCase.module == module)
        .order_by(TestCase.priority.asc(), TestCase.name)
    )
    return list(result.scalars().all())


async def create_test_case(db: AsyncSession, case: TestCaseCreate) -> TestCase:
    """创建测试用例"""
    data = case.model_dump()
    data["tags"] = ",".join(data.get("tags", []))
    db_case = TestCase(**data)
    db.add(db_case)
    await db.commit()
    await db.refresh(db_case)
    if db_case.directory_id:
        await update_directory_case_count(db, db_case.directory_id)
    return db_case


async def update_test_case(
    db: AsyncSession, case_id: int, case: TestCaseUpdate
) -> Optional[TestCase]:
    """更新测试用例"""
    db_case = await get_test_case(db, case_id)
    if not db_case:
        return None

    old_directory_id = db_case.directory_id
    update_data = case.model_dump(exclude_unset=True)
    if "tags" in update_data:
        update_data["tags"] = ",".join(update_data["tags"])
    for key, value in update_data.items():
        setattr(db_case, key, value)

    db_case.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(db_case)

    # 目录变更时同步更新新旧目录的计数
    new_directory_id = db_case.directory_id
    if old_directory_id != new_directory_id:
        if old_directory_id:
            await update_directory_case_count(db, old_directory_id)
        if new_directory_id:
            await update_directory_case_count(db, new_directory_id)

    return db_case


async def delete_test_case(db: AsyncSession, case_id: int) -> bool:
    """删除测试用例"""
    db_case = await get_test_case(db, case_id)
    if not db_case:
        return False

    directory_id = db_case.directory_id
    await db.delete(db_case)
    await db.commit()
    if directory_id:
        await update_directory_case_count(db, directory_id)
    return True


async def get_test_case_stats(db: AsyncSession) -> dict:
    """获取测试用例统计"""
    result = await db.execute(select(TestCase))
    cases = list(result.scalars().all())

    total = len(cases)
    automated = sum(1 for c in cases if c.is_automated)
    flaky = sum(1 for c in cases if c.flaky)

    by_type = {}
    by_priority = {}
    by_status = {}
    by_module = {}

    for c in cases:
        # 按类型统计
        by_type[c.case_type] = by_type.get(c.case_type, 0) + 1
        # 按优先级统计
        by_priority[c.priority] = by_priority.get(c.priority, 0) + 1
        # 按状态统计
        by_status[c.status] = by_status.get(c.status, 0) + 1
        # 按模块统计
        if c.module:
            by_module[c.module] = by_module.get(c.module, 0) + 1

    return {
        "total": total,
        "automated": automated,
        "manual": total - automated,
        "flaky": flaky,
        "pass_rate": round(sum(c.passed_runs for c in cases) / max(sum(c.total_runs for c in cases), 1) * 100, 1),
        "by_type": by_type,
        "by_priority": by_priority,
        "by_status": by_status,
        "by_module": by_module,
    }


# ===================== 目录 CRUD =====================

async def get_directories(db: AsyncSession) -> List[Directory]:
    """获取目录列表"""
    result = await db.execute(
        select(Directory).order_by(Directory.sort_order.asc(), Directory.name)
    )
    return list(result.scalars().all())


async def get_directory(db: AsyncSession, directory_id: int) -> Optional[Directory]:
    """获取单个目录"""
    result = await db.execute(
        select(Directory).where(Directory.id == directory_id)
    )
    return result.scalar_one_or_none()


async def create_directory(db: AsyncSession, directory: DirectoryCreate) -> Directory:
    """创建目录"""
    db_dir = Directory(**directory.model_dump())
    db.add(db_dir)
    await db.commit()
    await db.refresh(db_dir)
    # 更新用例数量统计
    await update_directory_case_count(db, db_dir.id)
    return db_dir


async def update_directory(
    db: AsyncSession, directory_id: int, directory: DirectoryUpdate
) -> Optional[Directory]:
    """更新目录"""
    db_dir = await get_directory(db, directory_id)
    if not db_dir:
        return None

    update_data = directory.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_dir, key, value)

    db_dir.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(db_dir)
    return db_dir


async def delete_directory(db: AsyncSession, directory_id: int) -> bool:
    """删除目录"""
    db_dir = await get_directory(db, directory_id)
    if not db_dir:
        return False
    
    # 将该目录下的用例移至无目录
    result = await db.execute(
        select(TestCase).where(TestCase.directory_id == directory_id)
    )
    cases = result.scalars().all()
    for case in cases:
        case.directory_id = None
    
    await db.delete(db_dir)
    await db.commit()
    return True


async def update_directory_case_count(db: AsyncSession, directory_id: int) -> None:
    """更新目录用例数量"""
    db_dir = await get_directory(db, directory_id)
    if not db_dir:
        return
    
    result = await db.execute(
        select(func.count()).select_from(TestCase).where(TestCase.directory_id == directory_id)
    )
    count = result.scalar() or 0
    db_dir.case_count = count
    db_dir.updated_at = datetime.utcnow()
    await db.commit()
