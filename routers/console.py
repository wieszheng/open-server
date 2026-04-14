"""控制台 API 路由"""
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas import TestExecutionCreate, TestExecutionResponse, ConsoleStats
import crud

router = APIRouter(prefix="/console", tags=["控制台"])


@router.get("/stats", response_model=ConsoleStats)
async def get_console_stats(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    """获取控制台统计数据"""
    return await crud.get_console_stats(db, days)


@router.get("/executions", response_model=List[TestExecutionResponse])
async def list_executions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """获取测试执行记录列表"""
    return await crud.get_test_executions(db, skip, limit)


@router.post("/executions", response_model=TestExecutionResponse, status_code=201)
async def create_execution(
    execution: TestExecutionCreate, db: AsyncSession = Depends(get_db)
):
    """创建测试执行记录"""
    return await crud.create_test_execution(db, execution)
