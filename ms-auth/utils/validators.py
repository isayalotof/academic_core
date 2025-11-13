"""
Data Validators
Валидация данных для аутентификации
"""

from typing import List, Dict, Any
import re


def validate_password_strength(password: str) -> List[str]:
    """
    Проверить надёжность пароля
    
    Args:
        password: Пароль для проверки
        
    Returns:
        Список ошибок валидации
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain special character")
    
    return errors


def validate_email(email: str) -> bool:
    """Валидация email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_username(username: str) -> List[str]:
    """Валидация username"""
    errors = []
    
    if len(username) < 3:
        errors.append("Username must be at least 3 characters")
    
    if len(username) > 50:
        errors.append("Username must be 50 characters or less")
    
    if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
        errors.append("Username can only contain letters, numbers, dots, underscores, and hyphens")
    
    return errors


def validate_register_data(data: Dict[str, Any]) -> List[str]:
    """
    Валидация данных регистрации
    
    Args:
        data: Данные запроса регистрации
        
    Returns:
        Список ошибок валидации
    """
    errors = []
    
    # Username
    if not data.get('username'):
        errors.append("Username is required")
    else:
        errors.extend(validate_username(data['username']))
    
    # Email
    if not data.get('email'):
        errors.append("Email is required")
    elif not validate_email(data['email']):
        errors.append("Invalid email format")
    
    # Password
    if not data.get('password'):
        errors.append("Password is required")
    else:
        errors.extend(validate_password_strength(data['password']))
    
    # Full name
    if not data.get('full_name'):
        errors.append("Full name is required")
    elif len(data['full_name']) < 2:
        errors.append("Full name must be at least 2 characters")
    elif len(data['full_name']) > 200:
        errors.append("Full name must be 200 characters or less")
    
    # Primary role
    valid_roles = ['student', 'teacher', 'staff', 'admin']
    if not data.get('primary_role'):
        errors.append("Primary role is required")
    elif data['primary_role'] not in valid_roles:
        errors.append(f"Primary role must be one of: {', '.join(valid_roles)}")
    
    return errors


def validate_login_data(data: Dict[str, Any]) -> List[str]:
    """Валидация данных входа"""
    errors = []
    
    if not data.get('username'):
        errors.append("Username or email is required")
    
    if not data.get('password'):
        errors.append("Password is required")
    
    return errors

