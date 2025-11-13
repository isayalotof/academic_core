"""
Data Validators
Валидация данных для аудиторий и запросов
"""

from typing import Dict, List, Optional, Any
import re


CLASSROOM_TYPES = {
    'LECTURE', 'SEMINAR', 'COMPUTER_LAB', 'LABORATORY', 
    'WORKSHOP', 'AUDITORIUM', 'GYM', 'LIBRARY'
}

VALID_DAYS = range(1, 7)  # 1-6 (Понедельник - Суббота)
VALID_TIME_SLOTS = range(1, 7)  # 1-6 пар


def validate_classroom_data(data: Dict[str, Any]) -> List[str]:
    """
    Валидация данных аудитории
    
    Args:
        data: Данные аудитории из запроса
        
    Returns:
        Список ошибок валидации (пустой если все ок)
    """
    errors = []
    
    # Name validation
    if not data.get('name') or len(data['name'].strip()) == 0:
        errors.append("Classroom name is required")
    elif len(data['name']) > 50:
        errors.append("Classroom name must be 50 characters or less")
    
    # Code validation
    if not data.get('code') or len(data['code'].strip()) == 0:
        errors.append("Classroom code is required")
    elif len(data['code']) > 20:
        errors.append("Classroom code must be 20 characters or less")
    elif not re.match(r'^[A-Z0-9_-]+$', data['code']):
        errors.append("Classroom code must contain only uppercase letters, numbers, underscores, and hyphens")
    
    # Building validation
    if not data.get('building_id'):
        errors.append("Building ID is required")
    elif not isinstance(data['building_id'], int) or data['building_id'] <= 0:
        errors.append("Building ID must be a positive integer")
    
    # Floor validation
    if data.get('floor') is None:
        errors.append("Floor is required")
    elif not isinstance(data['floor'], int):
        errors.append("Floor must be an integer")
    
    # Capacity validation
    if not data.get('capacity'):
        errors.append("Capacity is required")
    elif not isinstance(data['capacity'], int) or data['capacity'] <= 0:
        errors.append("Capacity must be a positive integer")
    elif data['capacity'] > 1000:
        errors.append("Capacity seems unrealistic (max 1000)")
    
    # Classroom type validation
    if not data.get('classroom_type'):
        errors.append("Classroom type is required")
    elif data['classroom_type'] not in CLASSROOM_TYPES:
        errors.append(f"Invalid classroom type. Must be one of: {', '.join(CLASSROOM_TYPES)}")
    
    # Computers count validation
    if data.get('has_computers') and data.get('computers_count', 0) <= 0:
        errors.append("If classroom has computers, computers_count must be specified")
    
    # Area validation
    if data.get('actual_area') is not None:
        if not isinstance(data['actual_area'], (int, float)) or data['actual_area'] <= 0:
            errors.append("Actual area must be a positive number")
    
    return errors


def validate_time_slot(day_of_week: int, time_slot: int) -> List[str]:
    """
    Валидация временного слота
    
    Args:
        day_of_week: День недели (1-6)
        time_slot: Номер пары (1-6)
        
    Returns:
        Список ошибок валидации
    """
    errors = []
    
    if day_of_week not in VALID_DAYS:
        errors.append(f"Day of week must be between 1 and 6 (got {day_of_week})")
    
    if time_slot not in VALID_TIME_SLOTS:
        errors.append(f"Time slot must be between 1 and 6 (got {time_slot})")
    
    return errors


def validate_reserve_request(data: Dict[str, Any]) -> List[str]:
    """
    Валидация запроса на бронирование
    
    Args:
        data: Данные запроса бронирования
        
    Returns:
        Список ошибок валидации
    """
    errors = []
    
    # Classroom ID validation
    if not data.get('classroom_id'):
        errors.append("Classroom ID is required")
    elif not isinstance(data['classroom_id'], int) or data['classroom_id'] <= 0:
        errors.append("Classroom ID must be a positive integer")
    
    # Time slot validation
    errors.extend(validate_time_slot(
        data.get('day_of_week', 0), 
        data.get('time_slot', 0)
    ))
    
    # Discipline name validation
    if not data.get('discipline_name') or len(data['discipline_name'].strip()) == 0:
        errors.append("Discipline name is required")
    elif len(data['discipline_name']) > 200:
        errors.append("Discipline name must be 200 characters or less")
    
    # Teacher name validation
    if data.get('teacher_name') and len(data['teacher_name']) > 200:
        errors.append("Teacher name must be 200 characters or less")
    
    # Group name validation
    if data.get('group_name') and len(data['group_name']) > 100:
        errors.append("Group name must be 100 characters or less")
    
    return errors


def validate_pagination(page: int, page_size: int) -> List[str]:
    """
    Валидация параметров пагинации
    
    Args:
        page: Номер страницы
        page_size: Размер страницы
        
    Returns:
        Список ошибок валидации
    """
    errors = []
    
    if page < 1:
        errors.append("Page must be >= 1")
    
    if page_size < 1:
        errors.append("Page size must be >= 1")
    elif page_size > 100:
        errors.append("Page size must be <= 100")
    
    return errors


def sanitize_search_query(query: Optional[str]) -> Optional[str]:
    """
    Санитизация поискового запроса
    
    Args:
        query: Поисковый запрос
        
    Returns:
        Очищенный запрос или None
    """
    if not query:
        return None
    
    # Remove extra whitespace
    query = ' '.join(query.split())
    
    # Limit length
    if len(query) > 100:
        query = query[:100]
    
    return query if query else None

