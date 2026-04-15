"""目录 API 路由"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated

from app.schemas import DirectoryCreate, DirectoryUpdate, DirectoryResponse
from app.services import DirectoryService
from app.dependencies import get_directory_service

router = APIRouter(prefix="/directories", tags=["目录管理"])


@router.get("", response_model=List[DirectoryResponse])
async def list_directories(
    service: DirectoryService = Depends(get_directory_service),
) -> List[DirectoryResponse]:
    """获取目录列表。"""
    return await service.get_directories()


@router.get("/{directory_id}", response_model=DirectoryResponse)
async def get_directory_detail(
    directory_id: Annotated[int, Path(ge=1, description="目录ID")],
    service: DirectoryService = Depends(get_directory_service),
) -> DirectoryResponse:
    """获取目录详情及其子目录。"""
    directory = await service.get_directory(directory_id)
    if not directory:
        raise HTTPException(status_code=404, detail="目录不存在")
    return directory


@router.get("/{directory_id}/children", response_model=List[DirectoryResponse])
async def get_directory_children(
    directory_id: Annotated[int, Path(ge=1, description="父目录ID")],
    service: DirectoryService = Depends(get_directory_service),
) -> List[DirectoryResponse]:
    """获取指定目录的所有子目录。"""
    parent = await service.get_directory(directory_id)
    if not parent:
        raise HTTPException(status_code=404, detail="父目录不存在")
    return await service.get_children(directory_id)


@router.post("", response_model=DirectoryResponse, status_code=201)
async def create_dir(
    directory: DirectoryCreate,
    service: DirectoryService = Depends(get_directory_service),
) -> DirectoryResponse:
    """创建目录。"""
    return await service.create_directory(directory)


@router.put("/{directory_id}", response_model=DirectoryResponse)
async def update_dir(
    directory_id: Annotated[int, Path(ge=1, description="目录ID")],
    directory: DirectoryUpdate,
    service: DirectoryService = Depends(get_directory_service),
) -> DirectoryResponse:
    """更新目录信息。"""
    db_dir = await service.update_directory(directory_id, directory)
    if not db_dir:
        raise HTTPException(status_code=404, detail="目录不存在")
    return db_dir


@router.delete("/{directory_id}", status_code=204)
async def delete_dir(
    directory_id: Annotated[int, Path(ge=1, description="目录ID")],
    service: DirectoryService = Depends(get_directory_service),
) -> None:
    """删除目录。"""
    success = await service.delete_directory(directory_id)
    if not success:
        raise HTTPException(status_code=404, detail="目录不存在")
