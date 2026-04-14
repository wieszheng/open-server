"""工作流 API 路由"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import json

from database import get_db
import crud_workflow as workflow_crud
import schemas_workflow as schemas

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("", response_model=List[schemas.WorkflowResponse])
async def list_workflows(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """获取工作流列表"""
    workflows = await workflow_crud.get_workflows(db, skip=skip, limit=limit)
    return workflows


@router.get("/test-case-ids", response_model=List[int])
async def get_workflowed_test_case_ids(db: AsyncSession = Depends(get_db)):
    """获取已有工作流的所有测试用例ID（用于标记已编排的用例）"""
    return await workflow_crud.get_workflowed_test_case_ids(db)


@router.get("/{test_case_id}")
async def get_workflow_by_test_case(
    test_case_id: int,
    db: AsyncSession = Depends(get_db),
):
    """根据测试用例ID获取工作流（不存在时返回 null）"""
    workflow = await workflow_crud.get_workflow_by_test_case(db, test_case_id)
    if workflow is None:
        return JSONResponse(content=json.loads("null"))
    return workflow


@router.post("/{test_case_id}", response_model=schemas.WorkflowResponse)
async def create_or_update_workflow(
    test_case_id: int,
    data: schemas.WorkflowCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建或更新工作流（根据测试用例ID）"""
    workflow = await workflow_crud.create_workflow(db, test_case_id, data)
    return workflow


@router.put("/{workflow_id}", response_model=schemas.WorkflowResponse)
async def update_workflow(
    workflow_id: int,
    data: schemas.WorkflowUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新工作流"""
    workflow = await workflow_crud.update_workflow(db, workflow_id, data)
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    return workflow


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: int,
    db: AsyncSession = Depends(get_db),
):
    """删除工作流"""
    success = await workflow_crud.delete_workflow(db, workflow_id)
    if not success:
        raise HTTPException(status_code=404, detail="工作流不存在")
    return {"message": "删除成功"}
