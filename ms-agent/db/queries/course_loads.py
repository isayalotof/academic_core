"""
SQL запросы для работы с нагрузкой
"""

# Вставка нагрузки
INSERT_COURSE_LOAD = """
    INSERT INTO course_loads (
        discipline_name, discipline_code,
        teacher_id, teacher_name, teacher_priority,
        group_id, group_name, group_size,
        lesson_type, hours_per_semester, lessons_per_week,
        semester, academic_year, source_file
    ) VALUES (
        %(discipline_name)s, %(discipline_code)s,
        %(teacher_id)s, %(teacher_name)s, %(teacher_priority)s,
        %(group_id)s, %(group_name)s, %(group_size)s,
        %(lesson_type)s, %(hours_per_semester)s, %(lessons_per_week)s,
        %(semester)s, %(academic_year)s, %(source_file)s
    )
    RETURNING id
"""

# Получить нагрузку по семестру
SELECT_COURSE_LOADS_BY_SEMESTER = """
    SELECT *
    FROM course_loads
    WHERE semester = %(semester)s
    ORDER BY teacher_priority ASC, teacher_name, discipline_name
"""

# Получить нагрузку конкретного преподавателя
SELECT_COURSE_LOADS_BY_TEACHER = """
    SELECT *
    FROM course_loads
    WHERE teacher_id = %(teacher_id)s AND semester = %(semester)s
    ORDER BY discipline_name
"""

# Получить нагрузку конкретной группы
SELECT_COURSE_LOADS_BY_GROUP = """
    SELECT *
    FROM course_loads
    WHERE group_id = %(group_id)s AND semester = %(semester)s
    ORDER BY discipline_name
"""

# Получить все нагрузки с фильтрами
SELECT_COURSE_LOADS_FILTERED = """
    SELECT *
    FROM course_loads
    WHERE semester = %(semester)s
        AND (%(teacher_ids)s IS NULL OR teacher_id = ANY(%(teacher_ids)s))
        AND (%(group_ids)s IS NULL OR group_id = ANY(%(group_ids)s))
    ORDER BY teacher_priority ASC, teacher_name, discipline_name
"""

# Подсчет нагрузки по преподавателю
COUNT_LESSONS_BY_TEACHER = """
    SELECT 
        teacher_id,
        teacher_name,
        teacher_priority,
        COUNT(*) as course_count,
        SUM(lessons_per_week) as total_lessons_per_week,
        SUM(hours_per_semester) as total_hours
    FROM course_loads
    WHERE semester = %(semester)s
    GROUP BY teacher_id, teacher_name, teacher_priority
    ORDER BY teacher_priority ASC, total_lessons_per_week DESC
"""

# Удалить нагрузку по семестру
DELETE_COURSE_LOADS_BY_SEMESTER = """
    DELETE FROM course_loads
    WHERE semester = %(semester)s
"""

# Получить статистику по приоритетам
SELECT_PRIORITY_STATISTICS = """
    SELECT 
        teacher_priority,
        COUNT(DISTINCT teacher_id) as teacher_count,
        COUNT(*) as course_count,
        SUM(lessons_per_week) as total_lessons
    FROM course_loads
    WHERE semester = %(semester)s
    GROUP BY teacher_priority
    ORDER BY teacher_priority
"""

