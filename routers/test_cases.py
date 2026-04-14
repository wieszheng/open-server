"""测试用例 API 路由"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from crud import (
    get_test_cases,
    get_test_case,
    create_test_case,
    update_test_case,
    delete_test_case,
    get_test_case_stats,
)
from schemas import TestCaseCreate, TestCaseUpdate, TestCaseResponse

router = APIRouter(prefix="/test-cases", tags=["测试用例"])


def convert_case_to_response(case) -> dict:
    """转换模型为响应格式"""
    return {
        "id": case.id,
        "name": case.name,
        "description": case.description,
        "case_type": case.case_type.value if hasattr(case.case_type, 'value') else case.case_type,
        "priority": case.priority.value if hasattr(case.priority, 'value') else case.priority,
        "status": case.status.value if hasattr(case.status, 'value') else case.status,
        "module": case.module,
        "directory_id": case.directory_id,
        "preconditions": case.preconditions,
        "test_steps": case.test_steps,
        "expected_results": case.expected_results,
        "author": case.author,
        "tags": case.get_tags_list(),
        "script_id": case.script_id,
        "is_automated": case.is_automated,
        "is_parallel": case.is_parallel,
        "total_runs": case.total_runs,
        "passed_runs": case.passed_runs,
        "failed_runs": case.failed_runs,
        "pass_rate": case.get_pass_rate(),
        "avg_duration": case.avg_duration,
        "last_run_time": case.last_run_time,
        "flaky": case.flaky,
        "created_at": case.created_at,
        "updated_at": case.updated_at,
    }


@router.get("", response_model=List[dict])
async def list_test_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    case_type: Optional[str] = Query(None, description="用例类型"),
    priority: Optional[str] = Query(None, description="优先级"),
    status: Optional[str] = Query(None, description="状态"),
    module: Optional[str] = Query(None, description="模块"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
):
    """获取测试用例列表"""
    cases = await get_test_cases(
        db,
        skip=skip,
        limit=limit,
        case_type=case_type,
        priority=priority,
        status=status,
        module=module,
        search=search,
    )
    return [convert_case_to_response(c) for c in cases]


@router.get("/stats", response_model=dict)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """获取测试用例统计"""
    return await get_test_case_stats(db)


@router.get("/{case_id}", response_model=dict)
async def get_test_case_detail(case_id: int, db: AsyncSession = Depends(get_db)):
    """获取测试用例详情"""
    case = await get_test_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="测试用例不存在")
    return convert_case_to_response(case)


@router.post("", response_model=dict, status_code=201)
async def create_case(case: TestCaseCreate, db: AsyncSession = Depends(get_db)):
    """创建测试用例"""
    db_case = await create_test_case(db, case)
    return convert_case_to_response(db_case)


@router.put("/{case_id}", response_model=dict)
async def update_case(
    case_id: int,
    case: TestCaseUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新测试用例"""
    db_case = await update_test_case(db, case_id, case)
    if not db_case:
        raise HTTPException(status_code=404, detail="测试用例不存在")
    return convert_case_to_response(db_case)


@router.delete("/{case_id}", status_code=204)
async def delete_case(case_id: int, db: AsyncSession = Depends(get_db)):
    """删除测试用例"""
    success = await delete_test_case(db, case_id)
    if not success:
        raise HTTPException(status_code=404, detail="测试用例不存在")
