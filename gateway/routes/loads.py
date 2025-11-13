"""
Course Loads Routes
REST API для управления учебной нагрузкой
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

class CreateCourseLoadRequest(BaseModel):
    """Запрос на создание учебной нагрузки"""
    teacher_id: Optional[int] = Field(None, gt=0, description="ID преподавателя (может быть NULL)")
    group_id: Optional[int] = Field(None, gt=0, description="ID группы (может быть NULL)")
    discipline_id: Optional[int] = Field(None, gt=0, description="ID дисциплины (может быть NULL)")
    discipline_name: str = Field(..., min_length=1, max_length=200, description="Название дисциплины")
    discipline_code: Optional[str] = Field(None, max_length=50, description="Код дисциплины")
    semester: int = Field(..., ge=1, le=12, description="Семестр обучения (1-12)")
    academic_year: str = Field(..., min_length=9, max_length=9, description="Формат: 2025/2026")
    hours_per_semester: int = Field(..., gt=0, description="Часов в семестр")
    lesson_type: str = Field(..., min_length=1, description="Тип занятия (любой непустой: Лекция, Практика, Консультация и т.д.)")
    classroom_requirements: Optional[str] = Field(None, max_length=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "teacher_id": 1,
                "group_id": 1,
                "discipline_id": 1,
                "discipline_name": "Математика",
                "discipline_code": "МАТ-101",
                "semester": 3,
                "academic_year": "2025/2026",
                "hours_per_semester": 68,
                "lesson_type": "Лекция",
                "classroom_requirements": "Проектор, компьютеры"
            }
        }


# ============ ENDPOINTS ============

@router.post("/course-loads", status_code=status.HTTP_201_CREATED)
async def create_course_load(
    request: CreateCourseLoadRequest,
    user: dict = Depends(get_current_user)
):
    """
    Создать запись учебной нагрузки
    
    **Требуется авторизация**
    
    Автоматически вычисляется lessons_per_week из hours_per_semester (триггер БД).
    """
    core_client = get_core_client()
    
    try:
        result = core_client.create_course_load(request.dict())
        
        return {
            "success": True,
            "course_load": result,
            "message": "Course load created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating course load: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create course load: {str(e)}"
        )


@router.get("/course-loads")
async def list_course_loads(
    semester: Optional[int] = Query(None, ge=1, le=12, description="Фильтр по семестру (1-12)"),
    academic_year: Optional[str] = Query(None, description="Фильтр по учебному году"),
    teacher_id: Optional[int] = Query(None, description="Фильтр по преподавателю"),
    group_id: Optional[int] = Query(None, description="Фильтр по группе"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(50, ge=1, le=100, description="Размер страницы"),
    user: dict = Depends(get_current_user)
):
    """
    Список учебной нагрузки с пагинацией
    
    **Требуется авторизация**
    
    Фильтры:
    - semester: 1-12 (семестр обучения)
    - academic_year: например "2025/2026"
    - teacher_id: ID преподавателя
    - group_id: ID группы
    """
    core_client = get_core_client()
    
    try:
        teacher_ids = [teacher_id] if teacher_id else None
        group_ids = [group_id] if group_id else None
        
        result = core_client.list_course_loads(
            page=page,
            page_size=page_size,
            semester=semester,
            academic_year=academic_year,
            teacher_ids=teacher_ids,
            group_ids=group_ids,
            only_active=True
        )
        
        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Error listing course loads: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list course loads: {str(e)}"
        )


@router.delete("/course-loads/{load_id}")
async def delete_course_load(
    load_id: int,
    user: dict = Depends(get_current_user)
):
    """
    Удалить запись учебной нагрузки
    
    **Требуется авторизация**
    """
    core_client = get_core_client()
    
    try:
        result = core_client.delete_course_load(load_id)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('message', 'Failed to delete course load')
            )
        
        return {
            "success": True,
            "message": result.get('message', 'Course load deleted successfully')
        }
    except Exception as e:
        logger.error(f"Error deleting course load: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete course load: {str(e)}"
        )


@router.get("/course-loads/summary")
async def get_course_loads_summary(
    semester: int = Query(..., ge=1, le=12, description="Семестр (1-12)"),
    academic_year: str = Query(..., description="Учебный год (например 2025/2026)"),
    user: dict = Depends(get_current_user)
):
    """
    Сводка по учебной нагрузке
    
    **Требуется авторизация**
    
    Возвращает:
    - Общее количество часов
    - Количество преподавателей
    - Количество групп
    - Количество дисциплин
    - Распределение по типам занятий
    """
    core_client = get_core_client()
    
    try:
        result = core_client.get_course_loads_summary(
            semester=semester,
            academic_year=academic_year
        )
        
        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Error getting summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get summary: {str(e)}"
        )

