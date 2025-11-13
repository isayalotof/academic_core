"""
Groups Routes
REST API для управления группами
"""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import Optional
import logging

from middleware.auth import get_current_user
from rpc_clients.core_client import get_core_client

logger = logging.getLogger(__name__)
router = APIRouter()


# ============ MODELS ============

class CreateGroupRequest(BaseModel):
    """Запрос на создание группы"""
    name: str = Field(..., min_length=1, max_length=50, description="Полное название группы")
    short_name: Optional[str] = Field(None, max_length=20, description="Короткое название")
    year: int = Field(..., ge=1, le=6, description="Курс (1-6)")
    semester: int = Field(..., ge=1, le=12, description="Текущий семестр обучения группы (1-12)")
    program_code: Optional[str] = Field(None, max_length=20)
    program_name: Optional[str] = Field(None, max_length=200)
    specialization: Optional[str] = Field(None, max_length=200)
    level: str = Field(..., description="bachelor, master, phd")
    curator_teacher_id: Optional[int] = None
    enrollment_date: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "ПИвКД-41",
                "short_name": "ПИвКД-41",
                "year": 4,
                "semester": 7,
                "program_code": "09.03.04",
                "program_name": "Программная инженерия",
                "specialization": "Веб-технологии и компьютерный дизайн",
                "level": "bachelor"
            }
        }


class UpdateGroupRequest(BaseModel):
    """Запрос на обновление группы"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    short_name: Optional[str] = Field(None, max_length=20)
    year: Optional[int] = Field(None, ge=1, le=6)
    semester: Optional[int] = Field(None, ge=1, le=12, description="Текущий семестр обучения группы (1-12)")
    program_code: Optional[str] = Field(None, max_length=20)
    program_name: Optional[str] = Field(None, max_length=200)
    specialization: Optional[str] = Field(None, max_length=200)
    curator_teacher_id: Optional[int] = None
    is_active: Optional[bool] = None


# ============ ENDPOINTS ============

@router.post("/groups", status_code=status.HTTP_201_CREATED)
async def create_group(
    request: CreateGroupRequest,
    user: dict = Depends(get_current_user)
):
    """
    Создать группу
    
    **Требуется авторизация**
    
    Автоматически:
    - size = 0 (обновляется при добавлении студентов)
    """
    core_client = get_core_client()
    
    try:
        result = core_client.create_group(request.dict())
        
        return {
            "success": True,
            "group": result,
            "message": "Group created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating group: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create group: {str(e)}"
        )


@router.get("/groups/{group_id}")
async def get_group(
    group_id: int,
    user: dict = Depends(get_current_user)
):
    """
    Получить группу по ID
    
    **Требуется авторизация**
    
    Возвращает:
    - Информацию о группе
    - Текущее количество студентов (size)
    - Куратора (если назначен)
    """
    core_client = get_core_client()
    
    try:
        result = core_client.get_group(group_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with id {group_id} not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting group: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get group: {str(e)}"
        )


@router.get("/groups")
async def list_groups(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(50, ge=1, le=100, description="Размер страницы"),
    year: Optional[int] = Query(None, ge=1, le=6, description="Фильтр по курсу"),
    level: Optional[str] = Query(None, description="Фильтр по уровню (bachelor/master/phd)"),
    only_active: bool = Query(True, description="Только активные"),
    user: dict = Depends(get_current_user)
):
    """
    Список групп с пагинацией
    
    **Требуется авторизация**
    
    Фильтры:
    - year: курс (1-6)
    - level: bachelor, master, phd
    - only_active: только активные группы
    """
    core_client = get_core_client()
    
    try:
        result = core_client.list_groups(
            page=page,
            page_size=page_size,
            year=year,
            level=level,
            only_active=only_active
        )
        return result
    except Exception as e:
        logger.error(f"Error listing groups: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list groups: {str(e)}"
        )


@router.put("/groups/{group_id}")
async def update_group(
    group_id: int,
    request: UpdateGroupRequest,
    user: dict = Depends(get_current_user)
):
    """
    Обновить группу
    
    **Требуется авторизация**
    """
    core_client = get_core_client()
    
    try:
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        result = core_client.update_group(group_id, update_data)
        
        return {
            "success": True,
            "group": result,
            "message": "Group updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating group: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update group: {str(e)}"
        )


@router.delete("/groups/{group_id}")
async def delete_group(
    group_id: int,
    user: dict = Depends(get_current_user)
):
    """
    Удалить группу (мягкое удаление)
    
    **Требуется авторизация**
    """
    core_client = get_core_client()
    
    try:
        result = core_client.delete_group(group_id)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('message', 'Failed to delete group')
            )
        
        return {
            "success": True,
            "message": result.get('message', 'Group deleted successfully')
        }
    except Exception as e:
        logger.error(f"Error deleting group: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete group: {str(e)}"
        )


@router.get("/groups/{group_id}/students")
async def get_group_students(
    group_id: int,
    user: dict = Depends(get_current_user)
):
    """
    Получить список студентов группы
    
    **Требуется авторизация**
    """
    core_client = get_core_client()
    
    try:
        result = core_client.get_group_students(group_id=group_id)
        return result
    except Exception as e:
        logger.error(f"Error getting group students: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get group students: {str(e)}"
        )

