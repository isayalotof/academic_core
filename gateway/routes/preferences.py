"""
⭐ Preferences Routes - KEY FEATURE!
REST API для управления предпочтениями преподавателей
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

from middleware.auth import get_current_user
from rpc_clients.core_client import get_core_client

logger = logging.getLogger(__name__)

router = APIRouter()


# ============ MODELS ============

class PreferenceItem(BaseModel):
    """Элемент предпочтения"""
    day_of_week: int = Field(..., ge=1, le=6, description="День недели (1=Пн, 6=Сб)")
    time_slot: int = Field(..., ge=1, le=6, description="Номер пары (1-6)")
    is_preferred: bool = Field(..., description="true=удобно, false=неудобно")
    preference_strength: Optional[str] = Field(None, description="'strong', 'medium', 'weak'")
    reason: Optional[str] = Field(None, description="Причина")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "day_of_week": 2,
                    "time_slot": 2,
                    "is_preferred": True,
                    "preference_strength": "strong",
                    "reason": "Удобное время для лекций"
                },
                {
                    "day_of_week": 4,
                    "time_slot": 1,
                    "is_preferred": False,
                    "preference_strength": "medium",
                    "reason": "Раннее время, неудобно добираться"
                },
                {
                    "day_of_week": 6,
                    "time_slot": 5,
                    "is_preferred": False,
                    "preference_strength": "weak",
                    "reason": "Суббота, предпочитаю не работать"
                }
            ]
        }


class SetPreferencesRequest(BaseModel):
    """Запрос на установку предпочтений"""
    preferences: List[PreferenceItem]
    replace_existing: bool = Field(False, description="Удалить существующие предпочтения")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "preferences": [
                        {
                            "day_of_week": 2,
                            "time_slot": 2,
                            "is_preferred": True,
                            "preference_strength": "strong"
                        },
                        {
                            "day_of_week": 2,
                            "time_slot": 3,
                            "is_preferred": True,
                            "preference_strength": "medium"
                        },
                        {
                            "day_of_week": 4,
                            "time_slot": 2,
                            "is_preferred": True,
                            "preference_strength": "strong"
                        },
                        {
                            "day_of_week": 6,
                            "time_slot": 5,
                            "is_preferred": False,
                            "preference_strength": "weak"
                        }
                    ],
                    "replace_existing": True
                }
            ]
        }


# ============ ENDPOINTS ============

@router.get("/teachers/{teacher_id}/preferences")
async def get_teacher_preferences(
    teacher_id: int,
    user: dict = Depends(get_current_user)
):
    """
    ⭐ Получить предпочтения преподавателя
    
    Возвращает:
    - Список предпочтений по дням и парам
    - Статистику (coverage, preferred/not_preferred count)
    - Информацию о преподавателе
    """
    core_client = get_core_client()
    
    try:
        result = core_client.get_teacher_preferences(teacher_id)
        
        return {
            "teacher_id": result['teacher_id'],
            "teacher_name": result['teacher_name'],
            "teacher_priority": result['teacher_priority'],
            "preferences": result['preferences'],
            "statistics": {
                "total_preferences": result['total_preferences'],
                "preferred_count": result['preferred_count'],
                "not_preferred_count": result['not_preferred_count'],
                "coverage_percentage": result['coverage_percentage']
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting preferences: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get preferences: {str(e)}"
        )


@router.post("/teachers/{teacher_id}/preferences")
async def set_teacher_preferences(
    teacher_id: int,
    request: SetPreferencesRequest,
    user: dict = Depends(get_current_user)
):
    """
    ⭐ Установить предпочтения преподавателя
    
    **Это KEY ENDPOINT для системы!**
    
    Пример запроса:
    ```json
    {
      "preferences": [
        {"day_of_week": 2, "time_slot": 2, "is_preferred": true},
        {"day_of_week": 2, "time_slot": 3, "is_preferred": true},
        {"day_of_week": 4, "time_slot": 2, "is_preferred": true},
        {"day_of_week": 6, "time_slot": 5, "is_preferred": false}
      ],
      "replace_existing": true
    }
    ```
    
    Где:
    - `day_of_week`: 1=Понедельник, 2=Вторник, ..., 6=Суббота
    - `time_slot`: 1-6 (номер пары)
    - `is_preferred`: true = удобное время, false = неудобное время
    """
    core_client = get_core_client()
    
    try:
        # Преобразовать в словари
        preferences = [pref.dict() for pref in request.preferences]
        
        result = core_client.set_teacher_preferences(
            teacher_id=teacher_id,
            preferences=preferences,
            replace_existing=request.replace_existing
        )
        
        return {
            "success": result['success'],
            "created_count": result['created_count'],
            "updated_count": result['updated_count'],
            "deleted_count": result['deleted_count'],
            "message": result['message']
        }
        
    except Exception as e:
        logger.error(f"Error setting preferences: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set preferences: {str(e)}"
        )


@router.delete("/teachers/{teacher_id}/preferences")
async def clear_teacher_preferences(
    teacher_id: int,
    user: dict = Depends(get_current_user)
):
    """
    Очистить все предпочтения преподавателя
    """
    core_client = get_core_client()
    
    try:
        result = core_client.clear_teacher_preferences(teacher_id)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('message', 'Failed to clear preferences')
            )
        
        return {
            "success": True,
            "deleted_count": result.get('deleted_count', 0),
            "message": result.get('message', 'Preferences cleared successfully')
        }
        
    except Exception as e:
        logger.error(f"Error clearing preferences: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear preferences: {str(e)}"
        )


@router.get("/preferences/grid")
async def get_preferences_grid(
    teacher_id: int,
    user: dict = Depends(get_current_user)
):
    """
    Получить предпочтения в виде сетки 6×6
    
    Возвращает матрицу:
    - `null`: предпочтение не установлено
    - `true`: удобное время
    - `false`: неудобное время
    
    Структура сетки:
    - grid[day][slot] где day = 0-5 (Пн-Сб), slot = 0-5 (1-6 пара)
    - grid[0][0] = Понедельник, 1 пара
    - grid[1][1] = Вторник, 2 пара
    """
    core_client = get_core_client()
    
    try:
        result = core_client.get_teacher_preferences(teacher_id)
        
        # Построить сетку 6×6 (дни × слоты)
        # grid[day][slot] где day=0-5 (Пн-Сб), slot=0-5 (1-6 пара)
        grid = [[None for _ in range(6)] for _ in range(6)]
        
        # Дополнительная информация о предпочтениях
        preferences_detail = []
        
        for pref in result['preferences']:
            day = pref['day_of_week'] - 1  # 0-based (1→0, 2→1, ..., 6→5)
            slot = pref['time_slot'] - 1    # 0-based (1→0, 2→1, ..., 6→5)
            
            # Валидация индексов
            if 0 <= day < 6 and 0 <= slot < 6:
                grid[day][slot] = pref['is_preferred']
                
                # Сохранить детали для дополнительной информации
                preferences_detail.append({
                    'day_of_week': pref['day_of_week'],
                    'day_name': ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"][day],
                    'time_slot': pref['time_slot'],
                    'slot_name': f"{pref['time_slot']} пара",
                    'is_preferred': pref['is_preferred'],
                    'preference_strength': pref.get('preference_strength'),
                    'reason': pref.get('reason')
                })
            else:
                logger.warning(
                    f"Invalid preference indices: day={day}, slot={slot} "
                    f"for teacher_id={teacher_id}"
                )
        
        return {
            "teacher_id": result['teacher_id'],
            "teacher_name": result['teacher_name'],
            "teacher_priority": result.get('teacher_priority'),
            "grid": grid,
            "preferences_detail": preferences_detail,
            "statistics": {
                "total_preferences": result.get('total_preferences', len(preferences_detail)),
                "preferred_count": result.get('preferred_count', sum(1 for p in preferences_detail if p['is_preferred'])),
                "not_preferred_count": result.get('not_preferred_count', sum(1 for p in preferences_detail if not p['is_preferred'])),
                "coverage_percentage": result.get('coverage_percentage', round(len(preferences_detail) / 36 * 100, 2))
            },
            "legend": {
                "days": ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"],
                "slots": ["1 пара", "2 пара", "3 пара", "4 пара", "5 пара", "6 пара"],
                "note": "grid[day][slot] где day=0-5 (Пн-Сб), slot=0-5 (1-6 пара)"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting preferences grid: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get preferences grid: {str(e)}"
        )

