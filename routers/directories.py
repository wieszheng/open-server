"""目录 API 路由"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from crud import (
    get_directories,
    get_directory,
    create_directory,
    update_directory,
    delete_directory,
)
from schemas import DirectoryCreate, DirectoryUpdate, DirectoryResponse

router = APIRouter(prefix="/directories", tags=["目录"])


@router.get("", response_model=List[DirectoryResponse])
async def list_directories(db: AsyncSession = Depends(get_db)):
    """获取目录列表"""
    return await get_directories(db)


@router.get("/{directory_id}", response_model=DirectoryResponse)
async def get_directory_detail(directory_id: int, db: AsyncSession = Depends(get_db)):
    """获取目录详情"""
    directory = await get_directory(db, directory_id)
    if not directory:
        raise HTTPException(status_code=404, detail="目录不存在")
    return directory


@router.post("", response_model=DirectoryResponse, status_code=201)
async def create_dir(directory: DirectoryCreate, db: AsyncSession = Depends(get_db)):
    """创建目录"""
    return await create_directory(db, directory)


@router.put("/{directory_id}", response_model=DirectoryResponse)
async def update_dir(
    directory_id: int,
    directory: DirectoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新目录"""
    db_dir = await update_directory(db, directory_id, directory)
    if not db_dir:
        raise HTTPException(status_code=404, detail="目录不存在")
    return db_dir


@router.delete("/{directory_id}", status_code=204)
async def delete_dir(directory_id: int, db: AsyncSession = Depends(get_db)):
    """删除目录"""
    success = await delete_directory(db, directory_id)
    if not success:
        raise HTTPException(status_code=404, detail="目录不存在")
