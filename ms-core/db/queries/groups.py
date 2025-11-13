"""
SQL queries for groups table
"""
from typing import Optional

# ============ CREATE ============

CREATE_GROUP = """
INSERT INTO groups (
    name, short_name,
    year, semester,
    program_code, program_name, specialization, level,
    curator_teacher_id, enrollment_date
)
VALUES (
    %(name)s, %(short_name)s,
    %(year)s, %(semester)s,
    %(program_code)s, %(program_name)s, %(specialization)s, %(level)s,
    %(curator_teacher_id)s, %(enrollment_date)s
)
RETURNING id, name, short_name, year, level, created_at;
"""

# ============ READ ============

GET_GROUP_BY_ID = """
SELECT 
    g.id, g.name, g.short_name,
    g.year, g.semester, g.size,
    g.program_code, g.program_name, g.specialization, g.level,
    g.curator_teacher_id,
    t.full_name as curator_name,
    g.is_active, g.enrollment_date, g.graduation_date,
    g.created_at, g.updated_at
FROM groups g
LEFT JOIN teachers t ON t.id = g.curator_teacher_id
WHERE g.id = %(group_id)s;
"""

GET_GROUP_BY_NAME = """
SELECT 
    g.id, g.name, g.short_name,
    g.year, g.semester, g.size,
    g.program_code, g.program_name, g.specialization, g.level,
    g.curator_teacher_id,
    t.full_name as curator_name,
    g.is_active, g.enrollment_date, g.graduation_date,
    g.created_at, g.updated_at
FROM groups g
LEFT JOIN teachers t ON t.id = g.curator_teacher_id
WHERE g.name = %(name)s;
"""

LIST_GROUPS = """
SELECT 
    g.id, g.name, g.short_name,
    g.year, g.semester, g.size,
    g.program_code, g.program_name, g.level,
    g.curator_teacher_id,
    t.full_name as curator_name,
    g.is_active,
    g.created_at
FROM groups g
LEFT JOIN teachers t ON t.id = g.curator_teacher_id
WHERE 1=1
    {filters}
ORDER BY {order_by}
LIMIT %(limit)s OFFSET %(offset)s;
"""

COUNT_GROUPS = """
SELECT COUNT(*) as total
FROM groups g
WHERE 1=1
    {filters};
"""

# ============ FILTERS & ORDER ============

def build_filters(
    year: Optional[int] = None,
    level: Optional[str] = None,
    only_active: bool = False
) -> str:
    """Построить WHERE фильтры для списка групп"""
    filters = []
    
    if year:
        filters.append(f"AND g.year = {year}")
    
    if level:
        filters.append(f"AND g.level = '{level}'")
    
    if only_active:
        filters.append("AND g.is_active = true")
    
    return ' '.join(filters)


def build_order_by(sort_by: str = 'created_at', sort_order: str = 'DESC') -> str:
    """Построить ORDER BY для списка групп"""
    valid_columns = ['name', 'year', 'level', 'created_at', 'updated_at']
    
    if sort_by not in valid_columns:
        sort_by = 'created_at'
    
    if sort_order.upper() not in ['ASC', 'DESC']:
        sort_order = 'DESC'
    
    return f"g.{sort_by} {sort_order}"

# ============ UPDATE ============

UPDATE_GROUP = """
UPDATE groups
SET
    name = COALESCE(%(name)s, name),
    semester = COALESCE(%(semester)s, semester),
    curator_teacher_id = COALESCE(%(curator_teacher_id)s, curator_teacher_id),
    is_active = COALESCE(%(is_active)s, is_active),
    updated_at = NOW()
WHERE id = %(group_id)s
RETURNING id, name, semester, is_active, updated_at;
"""

# ============ DELETE ============

DELETE_GROUP = """
DELETE FROM groups
WHERE id = %(group_id)s
RETURNING id, name;
"""

