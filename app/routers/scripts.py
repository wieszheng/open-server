"""脚本 API 路由"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import Annotated

from app.schemas import ScriptCreate, ScriptUpdate, ScriptResponse
from app.services import ScriptService
from app.dependencies import get_script_service

router = APIRouter(prefix="/scripts", tags=["脚本管理"])


@router.get("", response_model=List[ScriptResponse])
async def list_scripts(
    skip: Annotated[int, Query(ge=0, description="跳过的记录数")] = 0,
    limit: Annotated[int, Query(ge=1, le=500, description="返回的最大记录数")] = 100,
    category: Annotated[Optional[str], Query(description="按分类筛选")] = None,
    search: Annotated[Optional[str], Query(description="搜索关键词")] = None,
    service: ScriptService = Depends(get_script_service),
) -> List[ScriptResponse]:
    """获取脚本列表，支持分页、分类筛选和搜索。"""
    return await service.get_scripts(
        skip=skip, limit=limit, category=category, search=search
    )


@router.get("/featured", response_model=List[ScriptResponse])
async def list_featured_scripts(
    limit: Annotated[int, Query(ge=1, le=20, description="返回的最大记录数")] = 4,
    service: ScriptService = Depends(get_script_service),
) -> List[ScriptResponse]:
    """获取精选脚本列表。"""
    return await service.get_featured_scripts(limit=limit)


@router.get("/{script_id}", response_model=ScriptResponse)
async def get_script(
    script_id: Annotated[int, Path(ge=1, description="脚本ID")],
    service: ScriptService = Depends(get_script_service),
) -> ScriptResponse:
    """获取单个脚本详情。"""
    script = await service.get_script(script_id)
    if not script:
        raise HTTPException(status_code=404, detail="脚本不存在")
    return script


@router.post("", response_model=ScriptResponse, status_code=201)
async def create_script(
    script: ScriptCreate,
    service: ScriptService = Depends(get_script_service),
) -> ScriptResponse:
    """创建新脚本。"""
    return await service.create_script(script)


@router.put("/{script_id}", response_model=ScriptResponse)
async def update_script(
    script_id: Annotated[int, Path(ge=1, description="脚本ID")],
    script: ScriptUpdate,
    service: ScriptService = Depends(get_script_service),
) -> ScriptResponse:
    """更新脚本信息。"""
    updated = await service.update_script(script_id, script)
    if not updated:
        raise HTTPException(status_code=404, detail="脚本不存在")
    return updated


@router.delete("/{script_id}", status_code=204)
async def delete_script(
    script_id: Annotated[int, Path(ge=1, description="脚本ID")],
    service: ScriptService = Depends(get_script_service),
) -> None:
    """删除脚本。"""
    success = await service.delete_script(script_id)
    if not success:
        raise HTTPException(status_code=404, detail="脚本不存在")


@router.post("/{script_id}/views", response_model=ScriptResponse)
async def increment_views(
    script_id: Annotated[int, Path(ge=1, description="脚本ID")],
    service: ScriptService = Depends(get_script_service),
) -> ScriptResponse:
    """增加脚本浏览量。"""
    script = await service.increment_views(script_id)
    if not script:
        raise HTTPException(status_code=404, detail="脚本不存在")
    return script


@router.post("/{script_id}/downloads", response_model=ScriptResponse)
async def increment_downloads(
    script_id: Annotated[int, Path(ge=1, description="脚本ID")],
    service: ScriptService = Depends(get_script_service),
) -> ScriptResponse:
    """增加脚本下载量。"""
    script = await service.increment_downloads(script_id)
    if not script:
        raise HTTPException(status_code=404, detail="脚本不存在")
    return script
