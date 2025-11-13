"""
SQL queries for schedules table
Основные запросы для работы с расписанием
"""

# ============ SELECT QUERIES ============

GET_SCHEDULE_FOR_GROUP = """
    SELECT 
        s.*
    FROM schedules s
    WHERE 
        s.group_id = %(group_id)s
        AND s.semester = %(semester)s
        AND s.academic_year = %(academic_year)s
        AND (%(only_active)s = false OR s.is_active = true)
        AND (%(day_of_week)s IS NULL OR s.day_of_week = %(day_of_week)s)
        AND (%(week_type)s IS NULL OR s.week_type IN (%(week_type)s, 'both'))
    ORDER BY s.day_of_week, s.time_slot
"""

GET_SCHEDULE_FOR_TEACHER = """
    SELECT 
        s.*
    FROM schedules s
    WHERE 
        s.teacher_id = %(teacher_id)s
        AND s.semester = %(semester)s
        AND s.academic_year = %(academic_year)s
        AND (%(only_active)s = false OR s.is_active = true)
        AND (%(day_of_week)s IS NULL OR s.day_of_week = %(day_of_week)s)
        AND (%(week_type)s IS NULL OR s.week_type IN (%(week_type)s, 'both'))
    ORDER BY s.day_of_week, s.time_slot
"""

GET_SCHEDULE_FOR_CLASSROOM = """
    SELECT 
        s.*
    FROM schedules s
    WHERE 
        s.classroom_id = %(classroom_id)s
        AND s.semester = %(semester)s
        AND s.academic_year = %(academic_year)s
        AND (%(only_active)s = false OR s.is_active = true)
        AND (%(day_of_week)s IS NULL OR s.day_of_week = %(day_of_week)s)
        AND (%(week_type)s IS NULL OR s.week_type IN (%(week_type)s, 'both'))
    ORDER BY s.day_of_week, s.time_slot
"""

GET_SCHEDULE_FOR_DAY = """
    SELECT 
        s.*
    FROM schedules s
    WHERE 
        s.day_of_week = %(day_of_week)s
        AND s.semester = %(semester)s
        AND s.academic_year = %(academic_year)s
        AND s.is_active = true
        AND (%(week_type)s IS NULL OR s.week_type IN (%(week_type)s, 'both'))
        AND (%(group_ids)s IS NULL OR s.group_id = ANY(%(group_ids)s))
        AND (%(teacher_ids)s IS NULL OR s.teacher_id = ANY(%(teacher_ids)s))
        AND (%(classroom_ids)s IS NULL OR s.classroom_id = ANY(%(classroom_ids)s))
    ORDER BY s.time_slot, s.group_name
"""

GET_LESSON_BY_ID = """
    SELECT * FROM schedules WHERE id = %(id)s
"""

# ============ SEARCH ============

SEARCH_SCHEDULE = """
    SELECT 
        s.*,
        ts_rank(
            to_tsvector('russian', 
                coalesce(s.discipline_name, '') || ' ' || 
                coalesce(s.teacher_name, '') || ' ' || 
                coalesce(s.group_name, '')
            ),
            plainto_tsquery('russian', %(query)s)
        ) as rank
    FROM schedules s
    WHERE 
        s.semester = %(semester)s
        AND s.academic_year = %(academic_year)s
        AND to_tsvector('russian', 
            coalesce(s.discipline_name, '') || ' ' || 
            coalesce(s.teacher_name, '') || ' ' || 
            coalesce(s.group_name, '')
        ) @@ plainto_tsquery('russian', %(query)s)
    ORDER BY rank DESC
    LIMIT %(limit)s
"""

# ============ INSERT ============

INSERT_LESSON = """
    INSERT INTO schedules (
        day_of_week, time_slot, week_type,
        discipline_name, discipline_code,
        teacher_id, teacher_name,
        group_id, group_name, group_size,
        classroom_id, classroom_name, building_name,
        lesson_type, semester, academic_year,
        start_time, end_time,
        notes, is_active, generation_id, created_by
    ) VALUES (
        %(day_of_week)s, %(time_slot)s, %(week_type)s,
        %(discipline_name)s, %(discipline_code)s,
        %(teacher_id)s, %(teacher_name)s,
        %(group_id)s, %(group_name)s, %(group_size)s,
        %(classroom_id)s, %(classroom_name)s, %(building_name)s,
        %(lesson_type)s, %(semester)s, %(academic_year)s,
        %(start_time)s, %(end_time)s,
        %(notes)s, %(is_active)s, %(generation_id)s, %(created_by)s
    )
    RETURNING *
"""

# Для bulk insert - template для execute_values
BULK_INSERT_TEMPLATE = """(
    %(day_of_week)s, %(time_slot)s, %(week_type)s,
    %(discipline_name)s, %(discipline_code)s,
    %(teacher_id)s, %(teacher_name)s,
    %(group_id)s, %(group_name)s, %(group_size)s,
    %(classroom_id)s, %(classroom_name)s, %(building_name)s,
    %(lesson_type)s, %(semester)s, %(academic_year)s,
    %(start_time)s, %(end_time)s,
    %(generation_id)s, %(is_active)s, %(created_by)s
)"""

# ============ UPDATE ============

UPDATE_LESSON = """
    UPDATE schedules
    SET 
        day_of_week = COALESCE(%(day_of_week)s, day_of_week),
        time_slot = COALESCE(%(time_slot)s, time_slot),
        week_type = COALESCE(%(week_type)s, week_type),
        classroom_id = COALESCE(%(classroom_id)s, classroom_id),
        classroom_name = COALESCE(%(classroom_name)s, classroom_name),
        building_name = COALESCE(%(building_name)s, building_name),
        notes = COALESCE(%(notes)s, notes),
        updated_by = %(updated_by)s,
        updated_at = NOW()
    WHERE id = %(id)s
    RETURNING *
"""

# ============ DELETE ============

DELETE_LESSON = """
    DELETE FROM schedules WHERE id = %(id)s
"""

# ============ ACTIVATION ============

DEACTIVATE_SEMESTER_SCHEDULE = """
    UPDATE schedules 
    SET 
        is_active = false,
        updated_at = NOW(),
        updated_by = %(updated_by)s
    WHERE 
        semester = %(semester)s 
        AND academic_year = %(academic_year)s 
        AND is_active = true
"""

ACTIVATE_GENERATION_SCHEDULE = """
    UPDATE schedules 
    SET 
        is_active = true,
        updated_at = NOW()
    WHERE 
        generation_id = %(generation_id)s
        AND semester = %(semester)s
        AND academic_year = %(academic_year)s
"""

GET_GENERATION_COUNT = """
    SELECT COUNT(*) as count
    FROM schedules
    WHERE generation_id = %(generation_id)s
"""

# ============ STATISTICS ============

COUNT_ACTIVE_SCHEDULES = """
    SELECT 
        COUNT(*) as total,
        COUNT(DISTINCT teacher_id) as teachers,
        COUNT(DISTINCT group_id) as groups,
        COUNT(DISTINCT classroom_id) as classrooms
    FROM schedules
    WHERE 
        semester = %(semester)s
        AND academic_year = %(academic_year)s
        AND is_active = true
"""

GET_LESSONS_BY_TYPE = """
    SELECT 
        lesson_type,
        COUNT(*) as count
    FROM schedules
    WHERE 
        semester = %(semester)s
        AND academic_year = %(academic_year)s
        AND is_active = true
    GROUP BY lesson_type
    ORDER BY count DESC
"""

GET_LESSONS_PER_DAY = """
    SELECT 
        day_of_week,
        COUNT(*) as count
    FROM schedules
    WHERE 
        semester = %(semester)s
        AND academic_year = %(academic_year)s
        AND is_active = true
    GROUP BY day_of_week
    ORDER BY day_of_week
"""

