"""
SQL queries for students table
"""
from typing import Optional

# ============ CREATE ============

CREATE_STUDENT = """
INSERT INTO students (
    full_name, first_name, last_name, middle_name,
    student_number, group_id,
    email, phone,
    enrollment_date,
    status
)
VALUES (
    %(full_name)s, %(first_name)s, %(last_name)s, %(middle_name)s,
    %(student_number)s, %(group_id)s,
    %(email)s, %(phone)s,
    %(enrollment_date)s,
    COALESCE(%(status)s, 'active')
)
RETURNING id, full_name, student_number, group_id, status, created_at;
"""

# ============ READ ============

GET_STUDENT_BY_ID = """
SELECT 
    s.id, s.full_name, s.first_name, s.last_name, s.middle_name,
    s.student_number,
    s.group_id,
    g.name as group_name,
    s.email, s.phone,
    s.user_id,
    s.status, s.enrollment_date,
    s.created_at, s.updated_at
FROM students s
LEFT JOIN groups g ON g.id = s.group_id
WHERE s.id = %(student_id)s;
"""

GET_STUDENT_BY_NUMBER = """
SELECT 
    s.id, s.full_name, s.student_number,
    s.group_id, g.name as group_name,
    s.email, s.phone, s.user_id, s.status,
    s.created_at
FROM students s
LEFT JOIN groups g ON g.id = s.group_id
WHERE s.student_number = %(student_number)s;
"""

GET_STUDENT_BY_USER_ID = """
SELECT 
    s.id, s.full_name, s.student_number,
    s.group_id, g.name as group_name,
    s.email, s.phone, s.user_id, s.status,
    s.created_at
FROM students s
LEFT JOIN groups g ON g.id = s.group_id
WHERE s.user_id = %(user_id)s;
"""

LIST_STUDENTS = """
SELECT 
    s.id, s.full_name, s.student_number,
    s.group_id, g.name as group_name,
    s.email, s.status,
    s.created_at
FROM students s
LEFT JOIN groups g ON g.id = s.group_id
WHERE 1=1
    {filters}
ORDER BY {order_by}
LIMIT %(limit)s OFFSET %(offset)s;
"""

GET_GROUP_STUDENTS = """
SELECT 
    s.id, s.full_name, s.student_number,
    s.email, s.phone,
    s.status, s.enrollment_date,
    s.created_at
FROM students s
WHERE s.group_id = %(group_id)s
    AND (%(status)s IS NULL OR s.status = %(status)s)
ORDER BY s.full_name;
"""

COUNT_STUDENTS = """
SELECT COUNT(*) as total
FROM students s
WHERE 1=1
    {filters};
"""

# ============ FILTERS & ORDER ============

def build_filters(
    group_id: Optional[int] = None,
    status: Optional[str] = None
) -> str:
    """Построить WHERE фильтры для списка студентов"""
    filters = []
    
    if group_id:
        filters.append(f"AND s.group_id = {group_id}")
    
    if status:
        filters.append(f"AND s.status = '{status}'")
    
    return ' '.join(filters)


def build_order_by(sort_by: str = 'created_at', sort_order: str = 'DESC') -> str:
    """Построить ORDER BY для списка студентов"""
    valid_columns = ['full_name', 'student_number', 'created_at', 'updated_at']
    
    if sort_by not in valid_columns:
        sort_by = 'created_at'
    
    if sort_order.upper() not in ['ASC', 'DESC']:
        sort_order = 'DESC'
    
    return f"s.{sort_by} {sort_order}"

# ============ UPDATE ============

UPDATE_STUDENT = """
UPDATE students
SET
    full_name = COALESCE(%(full_name)s, full_name),
    group_id = COALESCE(%(group_id)s, group_id),
    email = COALESCE(%(email)s, email),
    phone = COALESCE(%(phone)s, phone),
    status = COALESCE(%(status)s, status),
    updated_at = NOW()
WHERE id = %(student_id)s
RETURNING id, full_name, group_id, status, updated_at;
"""

# ============ DELETE ============

DELETE_STUDENT = """
DELETE FROM students
WHERE id = %(student_id)s
RETURNING id, full_name;
"""

# ============ USER LINKS ============

LINK_STUDENT_TO_USER = """
UPDATE students
SET user_id = %(user_id)s, updated_at = NOW()
WHERE id = %(student_id)s
RETURNING id, full_name, user_id;
"""

