"""
Data validation utilities for ms-core
"""
import re
from typing import Any, Optional
from datetime import datetime


class ValidationError(Exception):
    """Validation error exception"""
    pass


def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address
    
    Returns:
        True if valid
    
    Raises:
        ValidationError: If invalid
    """
    if not email:
        return True  # Optional field
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError(f"Invalid email format: {email}")
    
    return True


def validate_phone(phone: str) -> bool:
    """
    Validate phone number
    
    Args:
        phone: Phone number
    
    Returns:
        True if valid
    """
    if not phone or phone in ('', 'None', 'null'):
        return True  # Optional field
    
    # Check if it's a placeholder or invalid string
    if phone.lower() in ('string', 'none', 'null', 'undefined'):
        raise ValidationError(f"Invalid phone number: {phone}")
    
    # Simple validation - at least 10 digits
    digits = re.sub(r'\D', '', phone)
    if len(digits) < 10:
        raise ValidationError(
            f"Invalid phone number: {phone} "
            "(must contain at least 10 digits)"
        )
    
    return True


def validate_employment_type(employment_type: str) -> bool:
    """
    Validate employment type
    
    Args:
        employment_type: Employment type
    
    Returns:
        True if valid
    
    Raises:
        ValidationError: If invalid
    """
    valid_types = ['external', 'graduate', 'internal', 'staff']
    if employment_type not in valid_types:
        raise ValidationError(
            f"Invalid employment type: {employment_type}. Must be one of: {valid_types}"
        )
    
    return True


def validate_day_of_week(day: int) -> bool:
    """
    Validate day of week (1-6)
    
    Args:
        day: Day of week
    
    Returns:
        True if valid
    
    Raises:
        ValidationError: If invalid
    """
    if not 1 <= day <= 6:
        raise ValidationError(f"Invalid day_of_week: {day}. Must be 1-6 (Mon-Sat)")
    
    return True


def validate_time_slot(slot: int) -> bool:
    """
    Validate time slot (1-6)
    
    Args:
        slot: Time slot number
    
    Returns:
        True if valid
    
    Raises:
        ValidationError: If invalid
    """
    if not 1 <= slot <= 6:
        raise ValidationError(f"Invalid time_slot: {slot}. Must be 1-6")
    
    return True


def validate_lesson_type(lesson_type: str) -> bool:
    """
    Validate lesson type
    
    Args:
        lesson_type: Lesson type
    
    Returns:
        True if valid
    
    Raises:
        ValidationError: If invalid
    """
    valid_types = ['Лекция', 'Практика', 'Лабораторная', 'Семинар']
    if lesson_type not in valid_types:
        raise ValidationError(
            f"Invalid lesson_type: {lesson_type}. Must be one of: {valid_types}"
        )
    
    return True


def validate_semester(semester: int) -> bool:
    """
    Validate semester (1 or 2)
    
    Args:
        semester: Semester number
    
    Returns:
        True if valid
    
    Raises:
        ValidationError: If invalid
    """
    if semester not in [1, 2]:
        raise ValidationError(f"Invalid semester: {semester}. Must be 1 or 2")
    
    return True


def validate_academic_year(academic_year: str) -> bool:
    """
    Validate academic year format (YYYY/YYYY)
    
    Args:
        academic_year: Academic year string
    
    Returns:
        True if valid
    
    Raises:
        ValidationError: If invalid
    """
    pattern = r'^\d{4}/\d{4}$'
    if not re.match(pattern, academic_year):
        raise ValidationError(
            f"Invalid academic_year format: {academic_year}. Must be YYYY/YYYY"
        )
    
    # Check that years are consecutive
    years = academic_year.split('/')
    if int(years[1]) != int(years[0]) + 1:
        raise ValidationError(
            f"Invalid academic_year: {academic_year}. Years must be consecutive"
        )
    
    return True


def validate_group_level(level: str) -> bool:
    """
    Validate group level
    
    Args:
        level: Group level
    
    Returns:
        True if valid
    
    Raises:
        ValidationError: If invalid
    """
    valid_levels = ['bachelor', 'master', 'postgraduate']
    if level not in valid_levels:
        raise ValidationError(
            f"Invalid level: {level}. Must be one of: {valid_levels}"
        )
    
    return True


def validate_student_status(status: str) -> bool:
    """
    Validate student status
    
    Args:
        status: Student status
    
    Returns:
        True if valid
    
    Raises:
        ValidationError: If invalid
    """
    valid_statuses = ['active', 'academic_leave', 'expelled', 'graduated']
    if status not in valid_statuses:
        raise ValidationError(
            f"Invalid status: {status}. Must be one of: {valid_statuses}"
        )
    
    return True


def validate_positive_integer(value: int, field_name: str = 'value') -> bool:
    """
    Validate positive integer
    
    Args:
        value: Value to validate
        field_name: Field name for error message
    
    Returns:
        True if valid
    
    Raises:
        ValidationError: If invalid
    """
    if not isinstance(value, int) or value <= 0:
        raise ValidationError(f"{field_name} must be a positive integer")
    
    return True


def validate_preference_strength(strength: Optional[str]) -> bool:
    """
    Validate preference strength
    
    Args:
        strength: Preference strength
    
    Returns:
        True if valid
    
    Raises:
        ValidationError: If invalid
    """
    if strength is None or strength == '':
        return True  # Optional
    
    valid_strengths = ['strong', 'medium', 'weak']
    if strength not in valid_strengths:
        raise ValidationError(
            f"Invalid preference_strength: {strength}. Must be one of: {valid_strengths}"
        )
    
    return True

