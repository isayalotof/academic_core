"""
Students Routes
REST API для управления студентами
"""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import logging
import grpc

from middleware.auth import get_current_user
from rpc_clients.core_client import get_core_client

logger = logging.getLogger(__name__)
router = APIRouter()


# ============ MODELS ============

class CreateStudentRequest(BaseModel):
    """Запрос на создание студента"""
    full_name: str = Field(..., min_length=1, max_length=200)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    student_number: str = Field(..., min_length=1, max_length=50, description="Номер студенческого билета")
    group_id: int = Field(..., gt=0, description="ID группы")
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    status: str = Field(default="active", description="active, academic_leave, expelled, graduated")
    enrollment_date: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Петров Пётр Петрович",
                "first_name": "Пётр",
                "last_name": "Петров",
                "middle_name": "Петрович",
                "student_number": "2024-123456",
                "group_id": 1,
                "email": "petrov@student.university.ru",
                "phone": "+7 (999) 888-77-66",
                "status": "active"
            }
        }


class UpdateStudentRequest(BaseModel):
    """Запрос на обновление студента"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    student_number: Optional[str] = Field(None, max_length=50)
    group_id: Optional[int] = Field(None, gt=0)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = None


# ============ ENDPOINTS ============

@router.post("/students", status_code=status.HTTP_201_CREATED)
async def create_student(
    request: CreateStudentRequest,
    user: dict = Depends(get_current_user)
):
    """
    Создать студента
    
    **Требуется авторизация**
    
    Автоматически:
    - Увеличивается group.size после добавления (триггер БД)
    """
    core_client = get_core_client()
    
    try:
        # Фильтруем поля: убираем status, так как его нет в CreateStudentRequest proto
        student_data = request.dict()
        student_data.pop('status', None)  # status устанавливается автоматически при создании
        
        result = core_client.create_student(student_data)
        
        return {
            "success": True,
            "student": result,
            "message": "Student created successfully"
        }
    except grpc.RpcError as e:
        logger.error(f"RPC error creating student: {e}")
        error_detail = e.details() or str(e)
        
        # Обработка специфичных ошибок
        if "foreign key constraint" in error_detail.lower() and "group_id" in error_detail.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Group with id {request.group_id} does not exist. Please create the group first."
            )
        elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
            raise HTTPException(status_code=400, detail=error_detail)
        elif e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail=error_detail)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create student: {error_detail}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating student: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create student: {str(e)}"
        )


@router.get("/students")
async def list_students(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(50, ge=1, le=100, description="Размер страницы"),
    group_id: Optional[int] = Query(None, description="Фильтр по группе"),
    status: Optional[str] = Query(None, description="Фильтр по статусу"),
    user: dict = Depends(get_current_user)
):
    """
    Список студентов с пагинацией
    
    **Требуется авторизация**
    
    Фильтры:
    - group_id: ID группы
    - status: active, academic_leave, expelled, graduated
    """
    core_client = get_core_client()
    
    try:
        result = core_client.list_students(
            page=page,
            page_size=page_size,
            group_id=group_id,
            status=status
        )
        return result
    except Exception as e:
        logger.error(f"Error listing students: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list students: {str(e)}"
        )


@router.get("/students/search")
async def search_students(
    q: str = Query(..., min_length=2, description="Поисковый запрос"),
    limit: int = Query(20, ge=1, le=100, description="Максимум результатов"),
    user: dict = Depends(get_current_user)
):
    """
    Поиск студентов
    
    **Требуется авторизация**
    
    Ищет по:
    - ФИО
    - Номеру студенческого билета
    - Email
    """
    core_client = get_core_client()
    
    try:
        # Поиск студентов через list_students с фильтрацией
        # В будущем можно добавить отдельный SearchStudents RPC
        # Пока используем существующий функционал
        result = core_client.list_students(
            page=1,
            page_size=limit,
            group_id=None,
            status=None
        )
        
        # Фильтрация по запросу (простая реализация)
        query_lower = q.lower()
        filtered_students = [
            s for s in result.get('students', [])
            if query_lower in s.get('full_name', '').lower() or
               query_lower in s.get('student_number', '').lower() or
               query_lower in s.get('email', '').lower()
        ]
        
        return {
            "students": filtered_students[:limit],
            "query": q,
            "total_found": len(filtered_students),
            "message": f"Found {len(filtered_students)} students"
        }
    except Exception as e:
        logger.error(f"Error searching students: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search students: {str(e)}"
        )


@router.get("/students/{student_id}")
async def get_student(
    student_id: int,
    user: dict = Depends(get_current_user)
):
    """
    Получить студента по ID
    
    **Требуется авторизация**
    """
    core_client = get_core_client()
    
    try:
        result = core_client.get_student(student_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with id {student_id} not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting student: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get student: {str(e)}"
        )


@router.put("/students/{student_id}")
async def update_student(
    student_id: int,
    request: UpdateStudentRequest,
    user: dict = Depends(get_current_user)
):
    """
    Обновить студента
    
    **Требуется авторизация**
    
    При изменении group_id автоматически обновляется размер обеих групп (триггер БД).
    """
    core_client = get_core_client()
    
    try:
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        result = core_client.update_student(student_id, update_data)
        
        return {
            "success": True,
            "student": result,
            "message": "Student updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating student: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update student: {str(e)}"
        )


@router.delete("/students/{student_id}")
async def delete_student(
    student_id: int,
    user: dict = Depends(get_current_user)
):
    """
    Удалить студента
    
    **Требуется авторизация**
    
    Автоматически уменьшается group.size (триггер БД).
    """
    core_client = get_core_client()
    
    try:
        result = core_client.delete_student(student_id)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('message', 'Failed to delete student')
            )
        
        return {
            "success": True,
            "message": result.get('message', 'Student deleted successfully')
        }
    except Exception as e:
        logger.error(f"Error deleting student: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete student: {str(e)}"
        )

