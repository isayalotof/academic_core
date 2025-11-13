"""
Teachers Routes
REST API для управления преподавателями
"""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import logging
import grpc
import re

from middleware.auth import get_current_user
from rpc_clients.core_client import get_core_client

logger = logging.getLogger(__name__)
router = APIRouter()


def sanitize_html(text: str) -> str:
    """
    Санитизировать HTML теги и JavaScript из текста
    
    Args:
        text: Текст для санитизации
        
    Returns:
        Санитизированный текст без HTML тегов и JavaScript
    """
    if not text:
        return text
    
    # Удалить все HTML теги
    text = re.sub(r'<[^>]+>', '', text)
    
    # Удалить потенциально опасные паттерны JavaScript
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    text = re.sub(r'alert\s*\([^)]*\)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'eval\s*\([^)]*\)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'script\s*:', '', text, flags=re.IGNORECASE)
    
    return text.strip()


# ============ MODELS ============

class CreateTeacherRequest(BaseModel):
    """Запрос на создание преподавателя"""
    full_name: str = Field(..., min_length=1, max_length=200)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    employment_type: str = Field(..., description="external, graduate, internal, staff")
    position: Optional[str] = Field(None, max_length=200)
    academic_degree: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=200)
    hire_date: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Иванов Иван Иванович",
                "first_name": "Иван",
                "last_name": "Иванов",
                "middle_name": "Иванович",
                "email": "ivanov@university.ru",
                "phone": "+7 (123) 456-78-90",
                "employment_type": "external",
                "position": "Профессор",
                "academic_degree": "Доктор наук",
                "department": "Кафедра ПИвКД"
            }
        }


class UpdateTeacherRequest(BaseModel):
    """Запрос на обновление преподавателя"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    employment_type: Optional[str] = None
    position: Optional[str] = Field(None, max_length=200)
    academic_degree: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None


# ============ ENDPOINTS ============

@router.post("/teachers", status_code=status.HTTP_201_CREATED)
async def create_teacher(
    request: CreateTeacherRequest,
    user: dict = Depends(get_current_user)
):
    """
    Создать преподавателя
    
    **Требуется авторизация**
    
    Автоматически вычисляется priority на основе employment_type:
    - external → priority = 1 (высший!)
    - graduate → priority = 2
    - internal → priority = 3
    - staff → priority = 4
    """
    core_client = get_core_client()
    
    try:
        # Санитизировать текстовые поля для защиты от XSS
        teacher_data = request.dict()
        text_fields = ['full_name', 'first_name', 'last_name', 'middle_name', 
                      'position', 'academic_degree', 'department']
        for field in text_fields:
            if field in teacher_data and teacher_data[field]:
                teacher_data[field] = sanitize_html(teacher_data[field])
        
        result = core_client.create_teacher(teacher_data)
        
        return {
            "success": True,
            "teacher": result,
            "message": "Teacher created successfully"
        }
    except grpc.RpcError as e:
        logger.error(f"RPC error creating teacher: {e}")
        # Обработка специфичных gRPC ошибок
        error_message = e.details() or "Unknown error"
        
        # Проверка на дубликат email
        if "duplicate key" in error_message and "teachers_email_key" in error_message:
            raise HTTPException(
                status_code=409,
                detail="Teacher with this email already exists"
            )
        # Проверка на ошибки валидации (могут приходить как INTERNAL)
        elif "Invalid" in error_message or "Validation" in error_message:
            raise HTTPException(status_code=400, detail=error_message)
        elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
            raise HTTPException(status_code=400, detail=error_message)
        elif e.code() == grpc.StatusCode.ALREADY_EXISTS:
            raise HTTPException(status_code=409, detail=error_message)
        else:
            raise HTTPException(
                status_code=500,
                detail="Teacher service error"
            )
    except Exception as e:
        logger.error(f"Error creating teacher: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create teacher: {str(e)}"
        )


@router.get("/teachers")
async def list_teachers(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(50, ge=1, le=100, description="Размер страницы"),
    employment_type: Optional[str] = Query(None, description="Фильтр по типу занятости"),
    department: Optional[str] = Query(None, description="Фильтр по кафедре"),
    only_active: bool = Query(True, description="Только активные"),
    user: dict = Depends(get_current_user)
):
    """
    Список преподавателей с пагинацией
    
    **Требуется авторизация**
    
    Фильтры:
    - employment_type: external, graduate, internal, staff
    - department: название кафедры
    - only_active: только активные преподаватели
    """
    core_client = get_core_client()
    
    try:
        result = core_client.list_teachers(
            page=page,
            page_size=page_size,
            employment_type=employment_type,
            department=department,
            only_active=only_active
        )
        
        return result
    except Exception as e:
        logger.error(f"Error listing teachers: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list teachers: {str(e)}"
        )


@router.get("/teachers/search")
async def search_teachers(
    q: str = Query(..., min_length=2, description="Поисковый запрос"),
    limit: int = Query(20, ge=1, le=100, description="Максимум результатов"),
    user: dict = Depends(get_current_user)
):
    """
    Поиск преподавателей
    
    **Требуется авторизация**
    
    Ищет по:
    - ФИО
    - Email
    - Кафедре
    """
    core_client = get_core_client()
    
    try:
        result = core_client.search_teachers(query=q, limit=limit)
        
        return {
            "teachers": result.get('teachers', []),
            "query": q,
            "total_found": result.get('total_count', 0),
            "message": f"Found {result.get('total_count', 0)} teachers"
        }
    except Exception as e:
        logger.error(f"Error searching teachers: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search teachers: {str(e)}"
        )


@router.get("/teachers/{teacher_id}")
async def get_teacher(
    teacher_id: int,
    include_preferences: bool = Query(False, description="Включить статистику предпочтений"),
    user: dict = Depends(get_current_user)
):
    """
    Получить преподавателя по ID
    
    **Требуется авторизация**
    
    Возвращает:
    - Базовую информацию о преподавателе
    - priority (1-4) вычислен автоматически
    - Если include_preferences=true, то статистику предпочтений
    """
    core_client = get_core_client()
    
    try:
        result = core_client.get_teacher(teacher_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Teacher with id {teacher_id} not found"
            )
        
        return result
    except HTTPException:
        raise
    except grpc.RpcError as e:
        logger.error(f"RPC error getting teacher: {e}")
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(
                status_code=404,
                detail=e.details() or f"Teacher with id {teacher_id} not found"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Teacher service error"
            )
    except Exception as e:
        logger.error(f"Error getting teacher: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get teacher: {str(e)}"
        )


@router.put("/teachers/{teacher_id}")
async def update_teacher(
    teacher_id: int,
    request: UpdateTeacherRequest,
    user: dict = Depends(get_current_user)
):
    """
    Обновить преподавателя
    
    **Требуется авторизация**
    
    Можно обновить любые поля.
    При изменении employment_type автоматически пересчитывается priority.
    """
    core_client = get_core_client()
    
    try:
        # Фильтруем только те поля, которые были переданы и не пустые
        update_data = {}
        for k, v in request.dict().items():
            if v is not None:
                # Валидация: не допускаем пустые строки для обязательных полей
                if isinstance(v, str) and v.strip() == "":
                    if k in ['full_name', 'email']:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Field '{k}' cannot be empty"
                        )
                update_data[k] = v
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Валидация employment_type если передан
        if 'employment_type' in update_data:
            valid_types = ['internal', 'external', 'graduate']
            if update_data['employment_type'] not in valid_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid employment_type. Must be one of: {', '.join(valid_types)}"
                )
        
        # Добавить updated_by
        update_data['updated_by'] = user.get('user_id', 0)
        
        result = core_client.update_teacher(teacher_id, update_data)
        
        return {
            "success": True,
            "teacher": result,
            "message": "Teacher updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating teacher: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update teacher: {str(e)}"
        )


@router.delete("/teachers/{teacher_id}")
async def delete_teacher(
    teacher_id: int,
    user: dict = Depends(get_current_user)
):
    """
    Удалить преподавателя (мягкое удаление)
    
    **Требуется авторизация**
    
    Устанавливает is_active = false вместо физического удаления.
    """
    core_client = get_core_client()
    
    try:
        result = core_client.delete_teacher(teacher_id, hard_delete=False)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('message', 'Failed to delete teacher')
            )
        
        return {
            "success": True,
            "message": result.get('message', 'Teacher deleted successfully')
        }
    except Exception as e:
        logger.error(f"Error deleting teacher: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete teacher: {str(e)}"
        )

