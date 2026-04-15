"""测试用例 API 路由"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import Annotated

from app.schemas import TestCaseCreate, TestCaseUpdate, TestCaseResponse
from app.services import TestCaseService, WorkflowService
from app.dependencies import get_test_case_service, get_workflow_service
from app.schemas.workflow import FlowUpsert, FlowResponse

router = APIRouter(prefix="/test-cases", tags=["测试用例管理"])


def convert_case_to_response(case) -> dict:
    """
    将 ORM 对象转换为响应字典。

    Args:
        case: 测试用例 ORM 对象。

    Returns:
        响应字典。
    """
    return {
        "id": case.id,
        "name": case.name,
        "description": case.description,
        "case_type": case.case_type.value if hasattr(case.case_type, "value") else case.case_type,
        "priority": case.priority.value if hasattr(case.priority, "value") else case.priority,
        "status": case.status.value if hasattr(case.status, "value") else case.status,
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


@router.get("", response_model=List[TestCaseResponse])
async def list_test_cases(
    skip: Annotated[int, Query(ge=0, description="跳过的记录数")] = 0,
    limit: Annotated[int, Query(ge=1, le=500, description="返回的最大记录数")] = 100,
    case_type: Annotated[Optional[str], Query(description="用例类型")] = None,
    priority: Annotated[Optional[str], Query(description="优先级")] = None,
    status: Annotated[Optional[str], Query(description="状态")] = None,
    module: Annotated[Optional[str], Query(description="模块")] = None,
    search: Annotated[Optional[str], Query(description="搜索关键词")] = None,
    service: TestCaseService = Depends(get_test_case_service),
) -> List[TestCaseResponse]:
    """获取测试用例列表，支持筛选和搜索。"""
    cases = await service.get_test_cases(
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
async def get_stats(
    service: TestCaseService = Depends(get_test_case_service),
) -> dict:
    """获取测试用例统计信息。"""
    return await service.get_test_case_stats()


@router.get("/{case_id}", response_model=TestCaseResponse)
async def get_test_case_detail(
    case_id: Annotated[int, Path(ge=1, description="测试用例ID")],
    service: TestCaseService = Depends(get_test_case_service),
) -> TestCaseResponse:
    """获取测试用例详情。"""
    case = await service.get_test_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="测试用例不存在")
    return convert_case_to_response(case)


@router.post("", response_model=TestCaseResponse, status_code=201)
async def create_case(
    case: TestCaseCreate,
    service: TestCaseService = Depends(get_test_case_service),
) -> TestCaseResponse:
    """创建测试用例。"""
    db_case = await service.create_test_case(case)
    return convert_case_to_response(db_case)


@router.put("/{case_id}", response_model=TestCaseResponse)
async def update_case(
    case_id: Annotated[int, Path(ge=1, description="测试用例ID")],
    case: TestCaseUpdate,
    service: TestCaseService = Depends(get_test_case_service),
) -> TestCaseResponse:
    """更新测试用例。"""
    db_case = await service.update_test_case(case_id, case)
    if not db_case:
        raise HTTPException(status_code=404, detail="测试用例不存在")
    return convert_case_to_response(db_case)


@router.delete("/{case_id}", status_code=204)
async def delete_case(
    case_id: Annotated[int, Path(ge=1, description="测试用例ID")],
    service: TestCaseService = Depends(get_test_case_service),
) -> None:
    """删除测试用例。"""
    success = await service.delete_test_case(case_id)
    if not success:
        raise HTTPException(status_code=404, detail="测试用例不存在")


@router.get("/{case_id}/flow", response_model=Optional[FlowResponse])
async def get_case_flow(
    case_id: Annotated[int, Path(ge=1, description="测试用例ID")],
    workflow_service: WorkflowService = Depends(get_workflow_service),
    test_case_service: TestCaseService = Depends(get_test_case_service),
) -> Optional[FlowResponse]:
    """
    获取测试用例的自动化工作流。
    - 存在：返回 { nodes, edges, updated_at }
    - 不存在：返回 null（前端按空画布处理）
    """
    case = await test_case_service.get_test_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="测试用例不存在")
    return await workflow_service.get_workflow_by_test_case(case_id)


@router.put("/{case_id}/flow", response_model=FlowResponse)
async def upsert_case_flow(
    case_id: Annotated[int, Path(ge=1, description="测试用例ID")],
    data: FlowUpsert,
    workflow_service: WorkflowService = Depends(get_workflow_service),
    test_case_service: TestCaseService = Depends(get_test_case_service),
) -> FlowResponse:
    """
    保存测试用例的自动化工作流（不存在时创建，存在时更新）。
    """
    case = await test_case_service.get_test_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="测试用例不存在")
    return await workflow_service.upsert_flow(case_id, data)
