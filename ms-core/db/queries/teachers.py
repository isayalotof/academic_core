"""
SQL queries for teachers table
БЕЗ ORM - только чистый SQL
"""
from typing import Dict, List, Any, Optional

# ============ CREATE ============

CREATE_TEACHER = """
INSERT INTO teachers (
    full_name, first_name, last_name, middle_name,
    email, phone,
    employment_type,
    position, academic_degree, department,
    hire_date, created_by
)
VALUES (
    %(full_name)s, %(first_name)s, %(last_name)s, %(middle_name)s,
    %(email)s, %(phone)s,
    %(employment_type)s,
    %(position)s, %(academic_degree)s, %(department)s,
    %(hire_date)s, %(created_by)s
)
RETURNING id, full_name, email, employment_type, priority, created_at;
"""

# ============ READ ============

GET_TEACHER_BY_ID = """
SELECT 
    t.id, t.full_name, t.first_name, t.last_name, t.middle_name,
    t.email, t.phone,
    t.employment_type, t.priority,
    t.position, t.academic_degree, t.department,
    t.user_id,
    t.is_active, t.hire_date, t.termination_date,
    t.created_at, t.updated_at,
    -- Статистика предпочтений (если нужно)
    COUNT(tp.id) FILTER (WHERE tp.is_preferred = true) as preferred_slots,
    COUNT(tp.id) as total_preferences,
    ROUND((COUNT(tp.id)::DECIMAL / 36 * 100), 2) as preferences_coverage
FROM teachers t
LEFT JOIN teacher_preferences tp ON tp.teacher_id = t.id
WHERE t.id = %(teacher_id)s
GROUP BY t.id;
"""

GET_TEACHER_BY_EMAIL = """
SELECT 
    id, full_name, first_name, last_name, middle_name,
    email, phone,
    employment_type, priority,
    position, academic_degree, department,
    user_id,
    is_active, hire_date, termination_date,
    created_at, updated_at
FROM teachers
WHERE email = %(email)s;
"""

GET_TEACHER_BY_USER_ID = """
SELECT 
    id, full_name, first_name, last_name, middle_name,
    email, phone,
    employment_type, priority,
    position, academic_degree, department,
    user_id,
    is_active, hire_date, termination_date,
    created_at, updated_at
FROM teachers
WHERE user_id = %(user_id)s;
"""

LIST_TEACHERS = """
SELECT 
    t.id, t.full_name, t.first_name, t.last_name,
    t.email, t.phone,
    t.employment_type, t.priority,
    t.position, t.academic_degree, t.department,
    t.user_id,
    t.is_active,
    t.created_at,
    COUNT(tp.id) FILTER (WHERE tp.is_preferred = true) as preferred_slots
FROM teachers t
LEFT JOIN teacher_preferences tp ON tp.teacher_id = t.id
WHERE 1=1
    {filters}
GROUP BY t.id
ORDER BY {order_by}
LIMIT %(limit)s OFFSET %(offset)s;
"""

COUNT_TEACHERS = """
SELECT COUNT(*) as total
FROM teachers t
WHERE 1=1
    {filters};
"""

# ============ SEARCH ============

SEARCH_TEACHERS = """
SELECT 
    id, full_name, email, phone,
    employment_type, priority,
    position, department,
    is_active
FROM teachers
WHERE to_tsvector('russian', coalesce(full_name, '') || ' ' || coalesce(email, '') || ' ' || coalesce(department, ''))
    @@ plainto_tsquery('russian', %(query)s)
    AND is_active = true
ORDER BY 
    ts_rank(
        to_tsvector('russian', coalesce(full_name, '') || ' ' || coalesce(email, '')),
        plainto_tsquery('russian', %(query)s)
    ) DESC
LIMIT %(limit)s;
"""

# ============ UPDATE ============

UPDATE_TEACHER = """
UPDATE teachers
SET
    full_name = COALESCE(%(full_name)s, full_name),
    email = COALESCE(%(email)s, email),
    phone = COALESCE(%(phone)s, phone),
    employment_type = COALESCE(%(employment_type)s, employment_type),
    position = COALESCE(%(position)s, position),
    department = COALESCE(%(department)s, department),
    is_active = COALESCE(%(is_active)s, is_active),
    updated_by = %(updated_by)s,
    updated_at = NOW()
WHERE id = %(teacher_id)s
RETURNING id, full_name, email, employment_type, priority, updated_at;
"""

# ============ DELETE ============

DELETE_TEACHER_SOFT = """
UPDATE teachers
SET is_active = false, termination_date = CURRENT_DATE, updated_at = NOW()
WHERE id = %(teacher_id)s
RETURNING id, full_name, is_active;
"""

DELETE_TEACHER_HARD = """
DELETE FROM teachers
WHERE id = %(teacher_id)s
RETURNING id, full_name;
"""

# ============ USER LINKS ============

LINK_TEACHER_TO_USER = """
UPDATE teachers
SET user_id = %(user_id)s, updated_at = NOW()
WHERE id = %(teacher_id)s
RETURNING id, full_name, user_id;
"""

UNLINK_TEACHER_FROM_USER = """
UPDATE teachers
SET user_id = NULL, updated_at = NOW()
WHERE id = %(teacher_id)s
RETURNING id, full_name, user_id;
"""

# ============ HELPER FUNCTIONS ============

def build_filters(
    employment_types: Optional[List[str]] = None,
    priorities: Optional[List[int]] = None,
    department: Optional[str] = None,
    only_active: bool = False
) -> str:
    """Построить WHERE фильтры для списка преподавателей"""
    filters = []
    
    if employment_types:
        types_str = "', '".join(employment_types)
        filters.append(f"AND t.employment_type IN ('{types_str}')")
    
    if priorities:
        priorities_str = ', '.join(map(str, priorities))
        filters.append(f"AND t.priority IN ({priorities_str})")
    
    if department:
        filters.append(f"AND t.department ILIKE '%{department}%'")
    
    if only_active:
        filters.append("AND t.is_active = true")
    
    return ' '.join(filters)


def build_order_by(sort_by: str = 'created_at', sort_order: str = 'DESC') -> str:
    """Построить ORDER BY для списка преподавателей"""
    valid_columns = ['full_name', 'email', 'priority', 'created_at', 'updated_at']
    
    if sort_by not in valid_columns:
        sort_by = 'created_at'
    
    if sort_order.upper() not in ['ASC', 'DESC']:
        sort_order = 'DESC'
    
    return f"t.{sort_by} {sort_order}"

