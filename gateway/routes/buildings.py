"""
Buildings Routes
REST API для управления зданиями
"""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import Optional
import logging
import grpc

from middleware.auth import get_current_user
from rpc_clients.classroom_client import classroom_client

logger = logging.getLogger(__name__)
router = APIRouter()


# ============ MODELS ============

class CreateBuildingRequest(BaseModel):
    """Запрос на создание здания"""
    name: str = Field(
        ..., min_length=1, max_length=200,
        description="Полное название здания"
    )
    short_name: Optional[str] = Field(
        None, max_length=50, description="Короткое название"
    )
    code: Optional[str] = Field(
        None, max_length=10, description="Код здания (A, B, C...)"
    )
    address: Optional[str] = Field(
        None, max_length=300, description="Адрес"
    )
    campus: Optional[str] = Field(
        None, max_length=100, description="Кампус"
    )
    latitude: Optional[float] = Field(None, description="Широта")
    longitude: Optional[float] = Field(None, description="Долгота")
    total_floors: Optional[int] = Field(
        1, ge=1, le=100, description="Количество этажей"
    )
    has_elevator: Optional[bool] = Field(
        False, description="Наличие лифта"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Главный корпус",
                "short_name": "ГК",
                "code": "A",
                "address": "ул. Университетская, д. 1",
                "campus": "Центральный",
                "latitude": 55.751244,
                "longitude": 37.618423,
                "total_floors": 5,
                "has_elevator": True
            }
        }


class UpdateBuildingRequest(BaseModel):
    """Запрос на обновление здания"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    short_name: Optional[str] = Field(None, max_length=50)
    code: Optional[str] = Field(None, max_length=10)
    address: Optional[str] = Field(None, max_length=300)
    campus: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_floors: Optional[int] = Field(None, ge=1, le=100)
    has_elevator: Optional[bool] = None


# ============ ENDPOINTS ============

@router.post("/buildings", status_code=status.HTTP_201_CREATED)
async def create_building(
    request: CreateBuildingRequest,
    user: dict = Depends(get_current_user)
):
    """
    Создать здание
    
    **Требуется авторизация**
    
    После создания можно добавлять аудитории в это здание.
    """
    try:
        # Подготовка данных для gRPC (убираем description, так как его нет в proto)
        building_data = request.dict()
        # description не поддерживается в proto, но можно добавить в будущем
        building_data.pop('description', None)
        
        logger.info(f"Creating building with data: {building_data}")
        result = classroom_client.create_building(building_data)
        
        return {
            "success": True,
            "building": result,
            "message": "Building created successfully"
        }
    except grpc.RpcError as e:
        logger.error(f"RPC error creating building: {e}", exc_info=True)
        error_message = e.details() or "Unknown error"
        error_code = e.code()
        
        # Check for duplicate code
        if ("duplicate key" in error_message.lower() and
                "buildings_code_key" in error_message.lower()):
            raise HTTPException(
                status_code=409,
                detail="Здание с таким кодом уже существует"
            )
        elif error_code == grpc.StatusCode.INVALID_ARGUMENT:
            raise HTTPException(status_code=400, detail=error_message or "Неверные данные для создания здания")
        elif error_code == grpc.StatusCode.ALREADY_EXISTS:
            raise HTTPException(status_code=409, detail=error_message or "Здание уже существует")
        elif error_code == grpc.StatusCode.UNAVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Сервис зданий временно недоступен. Попробуйте позже."
            )
        elif error_code == grpc.StatusCode.DEADLINE_EXCEEDED:
            raise HTTPException(
                status_code=504,
                detail="Превышено время ожидания ответа от сервиса зданий"
            )
        else:
            # Более информативное сообщение об ошибке
            detail_msg = error_message if error_message and error_message != "Unknown error" else f"Ошибка сервиса зданий (код: {error_code})"
            raise HTTPException(
                status_code=500,
                detail=detail_msg
            )
    except Exception as e:
        logger.error(f"Error creating building: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create building: {str(e)}"
        )


@router.get("/buildings/{building_id}")
async def get_building(
    building_id: int,
    user: dict = Depends(get_current_user)
):
    """
    Получить здание по ID
    
    **Требуется авторизация**
    
    Возвращает полную информацию о здании.
    """
    try:
        result = classroom_client.get_building(building_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Building with id {building_id} not found"
            )
        
        return result
    except HTTPException:
        raise
    except grpc.RpcError as e:
        logger.error(f"RPC error getting building: {e}")
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(
                status_code=404,
                detail=(
                    e.details() or
                    f"Building with id {building_id} not found"
                )
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Building service error"
            )
    except Exception as e:
        logger.error(f"Error getting building: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get building: {str(e)}"
        )


@router.get("/buildings")
async def list_buildings(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(50, ge=1, le=100, description="Размер страницы"),
    user: dict = Depends(get_current_user)
):
    """
    Список зданий
    
    **Требуется авторизация**
    
    Возвращает все здания в системе.
    """
    try:
        result = classroom_client.list_buildings()
        
        buildings = result['buildings']
        total_count = result['total_count']
        
        # Apply pagination (client-side for now)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_buildings = buildings[start:end]
        
        total_pages = (total_count + page_size - 1) // page_size
        
        return {
            "buildings": paginated_buildings,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Error listing buildings: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list buildings: {str(e)}"
        )


@router.put("/buildings/{building_id}")
async def update_building(
    building_id: int,
    request: UpdateBuildingRequest,
    user: dict = Depends(get_current_user)
):
    """
    Обновить здание
    
    **Требуется авторизация**
    
    Обновляет только переданные поля. Остальные остаются без изменений.
    """
    try:
        # Filter out None values
        update_data = {
            k: v for k, v in request.dict().items() if v is not None
        }
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        result = classroom_client.update_building(building_id, update_data)
        
        return {
            "success": True,
            "building": result,
            "message": "Building updated successfully"
        }
    except HTTPException:
        raise
    except grpc.RpcError as e:
        logger.error(f"RPC error updating building: {e}")
        error_message = e.details() or "Unknown error"
        
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(
                status_code=404,
                detail=f"Building with id {building_id} not found"
            )
        elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
            raise HTTPException(status_code=400, detail=error_message)
        elif ("duplicate key" in error_message and
                "buildings_code_key" in error_message):
            raise HTTPException(
                status_code=409,
                detail="Building with this code already exists"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Building service error"
            )
    except Exception as e:
        logger.error(f"Error updating building: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update building: {str(e)}"
        )


@router.delete("/buildings/{building_id}")
async def delete_building(
    building_id: int,
    user: dict = Depends(get_current_user)
):
    """
    Удалить здание
    
    **Требуется авторизация**
    
    **Внимание:** Здание нельзя удалить, если в нём есть активные аудитории.
    
    Возвращает:
    - 200: Здание успешно удалено
    - 404: Здание не найдено
    - 412: Невозможно удалить (есть активные аудитории)
    """
    try:
        success = classroom_client.delete_building(building_id)
        
        if success:
            return {
                "success": True,
                "message": "Building deleted successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete building"
            )
    except grpc.RpcError as e:
        logger.error(f"RPC error deleting building: {e}")
        error_message = e.details() or "Unknown error"
        
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(
                status_code=404,
                detail=f"Building with id {building_id} not found"
            )
        elif e.code() == grpc.StatusCode.FAILED_PRECONDITION:
            # Cannot delete due to existing classrooms
            raise HTTPException(
                status_code=412,
                detail=error_message
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Building service error"
            )
    except Exception as e:
        logger.error(f"Error deleting building: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete building: {str(e)}"
        )

