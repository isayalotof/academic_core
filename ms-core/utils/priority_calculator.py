"""
Расчёт приоритетов преподавателей
Логика для определения важности предпочтений в fitness-функции
"""

# ⭐ EMPLOYMENT TYPES И ИХ ПРИОРИТЕТЫ
# Это ключевая логика для LLM-агента!
# Чем ниже приоритет (1), тем важнее учитывать предпочтения преподавателя

EMPLOYMENT_PRIORITIES = {
    'external': {
        'priority': 1,
        'name': 'Внешний совместитель',
        'description': 'Работает на нескольких работах, ограниченная доступность',
        'penalty': -500,  # Максимальный штраф за нарушение предпочтения
        'color': '#FF5252'
    },
    'graduate': {
        'priority': 2,
        'name': 'Магистрант-преподаватель',
        'description': 'Учится и преподаёт, нужна гибкость',
        'penalty': -200,
        'color': '#FF9800'
    },
    'internal': {
        'priority': 3,
        'name': 'Внутренний совместитель',
        'description': 'Работает внутри университета на неполной ставке',
        'penalty': -100,
        'color': '#FFC107'
    },
    'staff': {
        'priority': 4,
        'name': 'Штатный преподаватель',
        'description': 'Постоянный сотрудник, гибкий график',
        'penalty': -30,  # Минимальный штраф
        'color': '#4CAF50'
    }
}


def get_priority_for_employment(employment_type: str) -> int:
    """
    Получить приоритет по типу занятости
    
    Args:
        employment_type: Тип занятости ('external', 'graduate', 'internal', 'staff')
    
    Returns:
        Приоритет (1-4), где 1 = высший приоритет
    """
    return EMPLOYMENT_PRIORITIES.get(employment_type, {}).get('priority', 4)


def get_penalty_for_priority(priority: int) -> int:
    """
    Получить штраф за нарушение предпочтения
    Используется в fitness-функции
    
    Args:
        priority: Приоритет преподавателя (1-4)
    
    Returns:
        Штраф (отрицательное число)
    """
    for emp_type, data in EMPLOYMENT_PRIORITIES.items():
        if data['priority'] == priority:
            return data['penalty']
    return -30  # Default


def get_penalty_for_employment(employment_type: str) -> int:
    """
    Получить штраф по типу занятости
    
    Args:
        employment_type: Тип занятости
    
    Returns:
        Штраф (отрицательное число)
    """
    return EMPLOYMENT_PRIORITIES.get(employment_type, {}).get('penalty', -30)


def get_priority_description(employment_type: str) -> str:
    """
    Получить описание приоритета
    
    Args:
        employment_type: Тип занятости
    
    Returns:
        Описание приоритета
    """
    return EMPLOYMENT_PRIORITIES.get(employment_type, {}).get('description', '')


def get_priority_name(employment_type: str) -> str:
    """
    Получить название типа занятости
    
    Args:
        employment_type: Тип занятости
    
    Returns:
        Название на русском
    """
    return EMPLOYMENT_PRIORITIES.get(employment_type, {}).get('name', employment_type)


def get_priority_color(employment_type: str) -> str:
    """
    Получить цвет для визуализации приоритета
    
    Args:
        employment_type: Тип занятости
    
    Returns:
        HEX код цвета
    """
    return EMPLOYMENT_PRIORITIES.get(employment_type, {}).get('color', '#9E9E9E')


def validate_employment_type(employment_type: str) -> bool:
    """
    Проверить валидность типа занятости
    
    Args:
        employment_type: Тип занятости
    
    Returns:
        True если валиден
    """
    return employment_type in EMPLOYMENT_PRIORITIES


def get_all_employment_types() -> list:
    """
    Получить список всех типов занятости
    
    Returns:
        Список типов
    """
    return list(EMPLOYMENT_PRIORITIES.keys())


def get_priority_info(employment_type: str) -> dict:
    """
    Получить полную информацию о приоритете
    
    Args:
        employment_type: Тип занятости
    
    Returns:
        Словарь с информацией
    """
    return EMPLOYMENT_PRIORITIES.get(employment_type, {
        'priority': 4,
        'name': 'Неизвестно',
        'description': '',
        'penalty': -30,
        'color': '#9E9E9E'
    })

