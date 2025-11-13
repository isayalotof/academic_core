"""
SQL queries for course_loads table
"""

# ============ CREATE ============

CREATE_COURSE_LOAD = """
INSERT INTO course_loads (
    discipline_id, discipline_name, discipline_code,
    teacher_id, teacher_name, teacher_priority,
    group_id, group_name, group_size,
    lesson_type, hours_per_semester, weeks_count,
    semester, academic_year,
    required_classroom_type, min_classroom_capacity,
    source, import_batch_id,
    created_by
)
SELECT 
    %(discipline_id)s,
    %(discipline_name)s, 
    %(discipline_code)s,
    %(teacher_id)s, 
    COALESCE(t.full_name, %(teacher_name)s), 
    COALESCE(t.priority, 2),
    %(group_id)s, 
    COALESCE(g.name, %(group_name)s), 
    COALESCE(g.size, %(group_size)s),
    %(lesson_type)s, 
    %(hours_per_semester)s, 
    COALESCE(%(weeks_count)s, 16),
    %(semester)s, 
    %(academic_year)s,
    %(required_classroom_type)s, 
    %(min_classroom_capacity)s,
    COALESCE(%(source)s, 'manual'), 
    %(import_batch_id)s,
    %(created_by)s
FROM (SELECT 1) dummy
LEFT JOIN teachers t ON t.id = %(teacher_id)s AND %(teacher_id)s IS NOT NULL AND %(teacher_id)s > 0
LEFT JOIN groups g ON g.id = %(group_id)s AND %(group_id)s IS NOT NULL AND %(group_id)s > 0
RETURNING id, discipline_name, teacher_name, group_name, lessons_per_week, created_at;
"""

# ============ READ ============

GET_COURSE_LOAD_BY_ID = """
SELECT 
    id, discipline_id, discipline_name, discipline_code,
    teacher_id, teacher_name, teacher_priority,
    group_id, group_name, group_size,
    lesson_type, hours_per_semester, weeks_count, lessons_per_week,
    semester, academic_year,
    required_classroom_type, min_classroom_capacity,
    is_active, source, import_batch_id,
    created_at
FROM course_loads
WHERE id = %(load_id)s;
"""

LIST_COURSE_LOADS = """
SELECT 
    id, discipline_name, discipline_code,
    teacher_id, teacher_name, teacher_priority,
    group_id, group_name, group_size,
    lesson_type, hours_per_semester, lessons_per_week,
    semester, academic_year,
    is_active, source,
    created_at
FROM course_loads
WHERE 1=1
    {filters}
ORDER BY teacher_name, group_name, discipline_name
LIMIT %(limit)s OFFSET %(offset)s;
"""

COUNT_COURSE_LOADS = """
SELECT COUNT(*) as total
FROM course_loads
WHERE 1=1
    {filters};
"""

# ============ DELETE ============

DELETE_COURSE_LOAD = """
DELETE FROM course_loads
WHERE id = %(load_id)s
RETURNING id, discipline_name;
"""

# ============ BATCH INSERT ============

BATCH_INSERT_COURSE_LOADS = """
INSERT INTO course_loads (
    discipline_name, discipline_code,
    teacher_id, teacher_name, teacher_priority,
    group_id, group_name, group_size,
    lesson_type, hours_per_semester, weeks_count, lessons_per_week,
    semester, academic_year,
    source, import_batch_id
)
VALUES %s
RETURNING id;
"""

# ============ HELPER FUNCTIONS ============

def build_course_load_filters(
    semester: int = None,
    academic_year: str = None,
    teacher_ids: list = None,
    group_ids: list = None,
    lesson_types: list = None,
    only_active: bool = False
) -> str:
    """Построить фильтры для списка нагрузки"""
    filters = []
    
    if semester is not None:
        filters.append(f"AND semester = {semester}")
    
    if academic_year:
        filters.append(f"AND academic_year = '{academic_year}'")
    
    if teacher_ids:
        # Фильтровать None значения
        non_null_ids = [tid for tid in teacher_ids if tid is not None]
        if non_null_ids:
            ids_str = ', '.join(map(str, non_null_ids))
            filters.append(f"AND teacher_id IN ({ids_str})")
        # Если в списке есть None, добавить условие для NULL
        if None in teacher_ids:
            filters.append("AND teacher_id IS NULL")
    
    if group_ids:
        # Фильтровать None значения
        non_null_ids = [gid for gid in group_ids if gid is not None]
        if non_null_ids:
            ids_str = ', '.join(map(str, non_null_ids))
            filters.append(f"AND group_id IN ({ids_str})")
        # Если в списке есть None, добавить условие для NULL
        if None in group_ids:
            filters.append("AND group_id IS NULL")
    
    if lesson_types:
        types_str = "', '".join(lesson_types)
        filters.append(f"AND lesson_type IN ('{types_str}')")
    
    if only_active:
        filters.append("AND is_active = true")
    
    return ' '.join(filters)

