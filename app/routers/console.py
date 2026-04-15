"""控制台 API 路由"""
from typing import List
from fastapi import APIRouter, Depends, Query
from typing import Annotated

from app.schemas import TestExecutionCreate, TestExecutionResponse, ConsoleStats
from app.services import ConsoleService
from app.dependencies import get_console_service

router = APIRouter(prefix="/console", tags=["控制台"])


@router.get("/stats", response_model=ConsoleStats)
async def get_console_stats(
    days: Annotated[int, Query(ge=1, le=90, description="统计天数")] = 7,
    service: ConsoleService = Depends(get_console_service),
) -> ConsoleStats:
    """获取控制台统计数据。"""
    return await service.get_console_stats(days=days)


@router.get("/executions", response_model=List[TestExecutionResponse])
async def list_executions(
    skip: Annotated[int, Query(ge=0, description="跳过的记录数")] = 0,
    limit: Annotated[int, Query(ge=1, le=500, description="返回的最大记录数")] = 100,
    service: ConsoleService = Depends(get_console_service),
) -> List[TestExecutionResponse]:
    """获取测试执行记录列表。"""
    return await service.get_executions(skip=skip, limit=limit)


@router.post("/executions", response_model=TestExecutionResponse, status_code=201)
async def create_execution(
    execution: TestExecutionCreate,
    service: ConsoleService = Depends(get_console_service),
) -> TestExecutionResponse:
    """创建测试执行记录。"""
    return await service.create_execution(execution)
