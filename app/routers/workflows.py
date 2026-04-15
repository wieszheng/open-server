"""工作流 API 路由"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from typing import Annotated
from fastapi.responses import JSONResponse
import json

from app.services import WorkflowService
from app.dependencies import get_workflow_service
from app.schemas.workflow import FlowUpsert, WorkflowResponse, WorkflowUpdate

router = APIRouter(prefix="/workflows", tags=["工作流管理"])


@router.get("", response_model=List[WorkflowResponse])
async def list_workflows(
    skip: Annotated[int, Query(ge=0, description="跳过的记录数")] = 0,
    limit: Annotated[int, Query(ge=1, le=500, description="返回的最大记录数")] = 100,
    service: WorkflowService = Depends(get_workflow_service),
) -> List[WorkflowResponse]:
    """获取工作流列表。"""
    return await service.get_workflows(skip=skip, limit=limit)


@router.get("/test-case-ids", response_model=List[int])
async def get_workflowed_test_case_ids(
    service: WorkflowService = Depends(get_workflow_service),
) -> List[int]:
    """获取已有工作流的所有测试用例ID（用于标记已编排的用例）。"""
    return await service.get_workflowed_test_case_ids()


@router.get("/{test_case_id}")
async def get_workflow_by_test_case(
    test_case_id: Annotated[int, Path(ge=1, description="测试用例ID")],
    service: WorkflowService = Depends(get_workflow_service),
):
    """根据测试用例ID获取工作流（不存在时返回 null）。"""
    workflow = await service.get_workflow_by_test_case(test_case_id)
    if workflow is None:
        return JSONResponse(content=json.loads("null"))
    return workflow


@router.post("/{test_case_id}", response_model=WorkflowResponse)
async def create_or_update_workflow(
    test_case_id: Annotated[int, Path(ge=1, description="测试用例ID")],
    data: FlowUpsert,
    service: WorkflowService = Depends(get_workflow_service),
) -> WorkflowResponse:
    """创建或更新工作流（根据测试用例ID）。"""
    return await service.upsert_flow(test_case_id, data)


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: Annotated[int, Path(ge=1, description="工作流ID")],
    data: WorkflowUpdate,
    service: WorkflowService = Depends(get_workflow_service),
) -> WorkflowResponse:
    """更新工作流信息。"""
    workflow = await service.update_workflow(workflow_id, data)
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    return workflow


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: Annotated[int, Path(ge=1, description="工作流ID")],
    service: WorkflowService = Depends(get_workflow_service),
) -> dict:
    """删除工作流。"""
    success = await service.delete_workflow(workflow_id)
    if not success:
        raise HTTPException(status_code=404, detail="工作流不存在")
    return {"message": "删除成功"}
