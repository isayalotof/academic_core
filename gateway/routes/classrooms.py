"""
Classroom REST Endpoints
HTTP REST API endpoints для управления аудиториями
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

from rpc_clients.classroom_client import classroom_client
from middleware.auth import get_current_user, require_staff, get_current_user_optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/classrooms", tags=["classrooms"])


# ============ REQUEST/RESPONSE MODELS ============

class CreateClassroomRequest(BaseModel):
    """Запрос на создание аудитории"""
    name: str = Field(..., min_length=1, max_length=50, description="Название аудитории")
    code: str = Field(..., min_length=1, max_length=20, description="Код аудитории")
    building_id: int = Field(..., gt=0, description="ID здания")
    floor: int = Field(..., description="Этаж")
    wing: Optional[str] = Field(None, max_length=50, description="Крыло")
    capacity: int = Field(..., gt=0, description="Вместимость")
    actual_area: Optional[float] = Field(None, gt=0, description="Площадь в кв.м")
    classroom_type: str = Field(..., description="Тип аудитории")
    
    # Equipment
    has_projector: bool = False
    has_whiteboard: bool = False
    has_blackboard: bool = False
    has_markers: bool = False
    has_chalk: bool = False
    has_computers: bool = False
    computers_count: int = 0
    has_audio_system: bool = False
    has_video_recording: bool = False
    has_air_conditioning: bool = False
    
    # Features
    is_accessible: bool = True
    has_windows: bool = True
    description: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "name": "Аудитория 101",
                    "code": "A-101",
                    "building_id": 1,
                    "floor": 1,
                    "wing": "Левое",
                    "capacity": 30,
                    "actual_area": 50.5,
                    "classroom_type": "LECTURE",
                    "has_projector": True,
                    "has_whiteboard": True,
                    "has_computers": False,
                    "is_accessible": True,
                    "has_windows": True,
                    "description": "Лекционная аудитория с проектором"
                },
                {
                    "name": "Лаборатория 205",
                    "code": "A-205",
                    "building_id": 1,
                    "floor": 2,
                    "capacity": 20,
                    "actual_area": 40.0,
                    "classroom_type": "LAB",
                    "has_projector": True,
                    "has_computers": True,
                    "computers_count": 20,
                    "has_air_conditioning": True,
                    "description": "Компьютерная лаборатория"
                }
            ]
        }


class UpdateClassroomRequest(BaseModel):
    """Запрос на обновление аудитории"""
    updates: Dict[str, str] = Field(..., description="Обновления (ключ-значение)")


class ReserveClassroomRequest(BaseModel):
    """Запрос на бронирование аудитории"""
    classroom_id: int = Field(..., gt=0)
    day_of_week: int = Field(..., ge=1, le=6, description="День недели (1-6)")
    time_slot: int = Field(..., ge=1, le=6, description="Номер пары (1-6)")
    week: int = Field(..., ge=1, le=16, description="Номер недели в семестре (1-16)")
    schedule_id: Optional[int] = None
    discipline_name: str = Field(..., min_length=1, max_length=200)
    teacher_name: Optional[str] = Field(None, max_length=200)
    group_name: Optional[str] = Field(None, max_length=100)
    lesson_type: Optional[str] = Field(None, max_length=50)
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "classroom_id": 1,
                    "day_of_week": 2,
                    "time_slot": 2,
                    "week": 1,
                    "discipline_name": "Математика",
                    "teacher_name": "Иванов Иван Иванович",
                    "group_name": "ПИвКД-41",
                    "lesson_type": "Лекция"
                },
                {
                    "classroom_id": 2,
                    "day_of_week": 4,
                    "time_slot": 3,
                    "week": 5,
                    "discipline_name": "Физика",
                    "teacher_name": "Петров Пётр Петрович",
                    "group_name": "ПИвКД-42",
                    "lesson_type": "Практика"
                }
            ]
        }


# ============ ENDPOINTS ============

@router.post("/", status_code=201)
async def create_classroom(
    data: CreateClassroomRequest,
    current_user: Dict[str, Any] = Depends(require_staff)
) -> Dict[str, Any]:
    """
    Создать новую аудиторию
    
    Требуется роль: staff или admin
    """
    import grpc
    
    try:
        request_data = data.dict()
        request_data['created_by'] = current_user.get('user_id')
        
        result = classroom_client.create_classroom(request_data)
        return result
        
    except grpc.RpcError as e:
        logger.error(f"Error creating classroom: {e}")
        # Обработка специфичных gRPC ошибок
        if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
            raise HTTPException(status_code=400, detail=e.details() or "Invalid request data")
        elif e.code() == grpc.StatusCode.NOT_FOUND:
            # Foreign key violation (building not found)
            raise HTTPException(status_code=404, detail=e.details() or "Referenced resource not found")
        elif e.code() == grpc.StatusCode.ALREADY_EXISTS:
            raise HTTPException(status_code=409, detail=e.details() or "Classroom already exists")
        else:
            # Проверить, есть ли в деталях информация о foreign key
            details = e.details() or ""
            if "foreign key" in details.lower() or "not found" in details.lower():
                raise HTTPException(status_code=400, detail=details)
            raise HTTPException(status_code=500, detail=details or "Classroom service error")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating classroom: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/code/{code}")
async def get_classroom_by_code(
    code: str = Path(..., description="Код аудитории"),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Получить информацию об аудитории по коду
    
    Доступно всем
    """
    try:
        classroom = classroom_client.get_classroom(code=code)
        
        if not classroom:
            raise HTTPException(status_code=404, detail="Classroom not found")
        
        return {
            "success": True,
            "classroom": classroom
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting classroom by code: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{classroom_id}")
async def get_classroom(
    classroom_id: int = Path(..., gt=0, description="ID аудитории"),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Получить информацию об аудитории по ID
    
    Доступно всем (включая неавторизованных)
    """
    try:
        classroom = classroom_client.get_classroom(classroom_id=classroom_id)
        
        if not classroom:
            raise HTTPException(status_code=404, detail="Classroom not found")
        
        return {
            "success": True,
            "classroom": classroom
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting classroom: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{classroom_id}")
async def update_classroom(
    classroom_id: int = Path(..., gt=0),
    data: UpdateClassroomRequest = ...,
    current_user: Dict[str, Any] = Depends(require_staff)
) -> Dict[str, Any]:
    """
    Обновить аудиторию
    
    Требуется роль: staff или admin
    """
    try:
        result = classroom_client.update_classroom(
            classroom_id,
            data.updates
        )
        return result
        
    except Exception as e:
        logger.error(f"Error updating classroom: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{classroom_id}")
async def delete_classroom(
    classroom_id: int = Path(..., gt=0),
    hard_delete: bool = Query(False, description="Физическое удаление"),
    current_user: Dict[str, Any] = Depends(require_staff)
) -> Dict[str, Any]:
    """
    Удалить аудиторию
    
    Требуется роль: staff или admin
    """
    try:
        result = classroom_client.delete_classroom(classroom_id, hard_delete)
        return result
        
    except Exception as e:
        logger.error(f"Error deleting classroom: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_classrooms(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    search: Optional[str] = Query(None, description="Поисковый запрос"),
    building_ids: Optional[str] = Query(None, description="ID зданий через запятую"),
    classroom_types: Optional[str] = Query(None, description="Типы через запятую"),
    min_capacity: Optional[int] = Query(None, ge=1),
    max_capacity: Optional[int] = Query(None, ge=1),
    sort_by: str = Query("name", description="Поле сортировки"),
    sort_order: str = Query("ASC", regex="^(ASC|DESC)$"),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Получить список аудиторий с фильтрацией
    
    Доступно всем
    """
    try:
        # Parse lists
        building_ids_list = [int(x) for x in building_ids.split(',')] if building_ids else None
        classroom_types_list = classroom_types.split(',') if classroom_types else None
        
        result = classroom_client.list_classrooms(
            page=page,
            page_size=page_size,
            search_query=search,
            building_ids=building_ids_list,
            classroom_types=classroom_types_list,
            min_capacity=min_capacity,
            max_capacity=max_capacity,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        logger.error(f"Error listing classrooms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available/search")
async def find_available_classrooms(
    day_of_week: int = Query(..., ge=1, le=6, description="День недели (1-6)"),
    time_slot: int = Query(..., ge=1, le=6, description="Номер пары (1-6)"),
    min_capacity: int = Query(1, ge=1, description="Минимальная вместимость"),
    need_projector: bool = Query(False),
    need_whiteboard: bool = Query(False),
    need_computers: bool = Query(False),
    building_ids: Optional[str] = Query(None, description="ID зданий через запятую"),
    classroom_types: Optional[str] = Query(None, description="Типы через запятую"),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Найти свободные аудитории
    
    Доступно всем
    """
    try:
        # Parse lists
        building_ids_list = [int(x) for x in building_ids.split(',')] if building_ids else None
        classroom_types_list = classroom_types.split(',') if classroom_types else None
        
        classrooms = classroom_client.find_available_classrooms(
            day_of_week=day_of_week,
            time_slot=time_slot,
            min_capacity=min_capacity,
            need_projector=need_projector,
            need_whiteboard=need_whiteboard,
            need_computers=need_computers,
            building_ids=building_ids_list,
            classroom_types=classroom_types_list
        )
        
        return {
            "success": True,
            "classrooms": classrooms,
            "total": len(classrooms)
        }
        
    except Exception as e:
        logger.error(f"Error finding available classrooms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{classroom_id}/availability")
async def check_availability(
    classroom_id: int = Path(..., gt=0),
    day_of_week: int = Query(..., ge=1, le=6),
    time_slot: int = Query(..., ge=1, le=6),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Проверить доступность аудитории
    
    Доступно всем
    """
    try:
        result = classroom_client.check_availability(
            classroom_id,
            day_of_week,
            time_slot
        )
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        logger.error(f"Error checking availability: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reserve")
async def reserve_classroom(
    data: ReserveClassroomRequest,
    current_user: Dict[str, Any] = Depends(require_staff)
) -> Dict[str, Any]:
    """
    Забронировать аудиторию
    
    Требуется роль: staff или admin
    """
    try:
        result = classroom_client.reserve_classroom(data.dict())
        return result
        
    except Exception as e:
        logger.error(f"Error reserving classroom: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{classroom_id}/schedule")
async def get_classroom_schedule(
    classroom_id: int = Path(..., gt=0),
    days: Optional[str] = Query(None, description="Дни недели через запятую (1-6)"),
    week: Optional[int] = Query(None, ge=1, le=16, description="Номер недели в семестре (1-16), если не указано - все недели"),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Получить расписание аудитории
    
    Доступно всем
    
    Параметры:
    - days: Фильтр по дням недели (опционально)
    - week: Фильтр по неделе в семестре (1-16), если не указано - показываются все недели
    """
    try:
        days_list = [int(x) for x in days.split(',')] if days else None
        
        result = classroom_client.get_schedule(classroom_id, days_list, week=week)
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        logger.error(f"Error getting schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/overall")
async def get_statistics(
    classroom_id: Optional[int] = Query(None, description="ID аудитории"),
    building_id: Optional[int] = Query(None, description="ID здания"),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Получить статистику
    
    Доступно всем
    """
    try:
        result = classroom_client.get_statistics(
            classroom_id=classroom_id,
            building_id=building_id
        )
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

