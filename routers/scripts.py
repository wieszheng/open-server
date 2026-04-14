"""脚本 API 路由"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas import ScriptCreate, ScriptUpdate, ScriptResponse
import crud

router = APIRouter(prefix="/scripts", tags=["脚本"])


@router.get("", response_model=List[ScriptResponse])
async def list_scripts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """获取脚本列表"""
    return await crud.get_scripts(db, skip, limit, category, search)


@router.get("/featured", response_model=List[ScriptResponse])
async def list_featured_scripts(
    limit: int = Query(4, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """获取精选脚本"""
    return await crud.get_featured_scripts(db, limit)


@router.get("/{script_id}", response_model=ScriptResponse)
async def get_script(script_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个脚本"""
    script = await crud.get_script(db, script_id)
    if not script:
        raise HTTPException(status_code=404, detail="脚本不存在")
    return script


@router.post("", response_model=ScriptResponse, status_code=201)
async def create_script(
    script: ScriptCreate, db: AsyncSession = Depends(get_db)
):
    """创建脚本"""
    return await crud.create_script(db, script)


@router.put("/{script_id}", response_model=ScriptResponse)
async def update_script(
    script_id: int,
    script: ScriptUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新脚本"""
    updated = await crud.update_script(db, script_id, script)
    if not updated:
        raise HTTPException(status_code=404, detail="脚本不存在")
    return updated


@router.delete("/{script_id}", status_code=204)
async def delete_script(script_id: int, db: AsyncSession = Depends(get_db)):
    """删除脚本"""
    success = await crud.delete_script(db, script_id)
    if not success:
        raise HTTPException(status_code=404, detail="脚本不存在")


@router.post("/{script_id}/views", response_model=ScriptResponse)
async def increment_views(script_id: int, db: AsyncSession = Depends(get_db)):
    """增加浏览量"""
    script = await crud.increment_script_views(db, script_id)
    if not script:
        raise HTTPException(status_code=404, detail="脚本不存在")
    return script


@router.post("/{script_id}/downloads", response_model=ScriptResponse)
async def increment_downloads(script_id: int, db: AsyncSession = Depends(get_db)):
    """增加下载量"""
    script = await crud.increment_script_downloads(db, script_id)
    if not script:
        raise HTTPException(status_code=404, detail="脚本不存在")
    return script
