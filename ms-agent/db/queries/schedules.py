"""
SQL запросы для работы с расписанием
"""

# Вставка расписания
INSERT_SCHEDULE = """
    INSERT INTO schedules (
        course_load_id, day_of_week, time_slot,
        classroom_id, classroom_name,
        teacher_id, teacher_name, group_id, group_name,
        discipline_name, lesson_type, generation_id, is_active,
        semester, academic_year
    ) VALUES (
        %(course_load_id)s, %(day_of_week)s, %(time_slot)s,
        %(classroom_id)s, %(classroom_name)s,
        %(teacher_id)s, %(teacher_name)s, %(group_id)s, %(group_name)s,
        %(discipline_name)s, %(lesson_type)s, %(generation_id)s, %(is_active)s,
        %(semester)s, %(academic_year)s
    )
    RETURNING id
"""

# Обновить временной слот
UPDATE_SCHEDULE_TIME = """
    UPDATE schedules
    SET day_of_week = %(day_of_week)s,
        time_slot = %(time_slot)s
    WHERE id = %(id)s
"""

# Обновить аудиторию
UPDATE_SCHEDULE_CLASSROOM = """
    UPDATE schedules
    SET classroom_id = %(classroom_id)s,
        classroom_name = %(classroom_name)s
    WHERE id = %(id)s
"""

# Получить активное расписание (только последнее сгенерированное)
SELECT_ACTIVE_SCHEDULES = """
    SELECT s.*
    FROM schedules s
    INNER JOIN (
        SELECT MAX(generation_id) as max_generation_id
        FROM schedules
        WHERE is_active = true AND generation_id IS NOT NULL
    ) latest ON s.generation_id = latest.max_generation_id
    WHERE s.is_active = true
    ORDER BY s.day_of_week, s.time_slot, s.teacher_name
"""

# Получить расписание по generation_id
SELECT_SCHEDULES_BY_GENERATION = """
    SELECT *
    FROM schedules
    WHERE generation_id = %(generation_id)s
    ORDER BY day_of_week, time_slot, teacher_name
"""

# Получить расписание преподавателя
SELECT_TEACHER_SCHEDULE = """
    SELECT *
    FROM schedules
    WHERE teacher_id = %(teacher_id)s AND is_active = true
        AND (%(day_of_week)s IS NULL OR day_of_week = %(day_of_week)s)
    ORDER BY day_of_week, time_slot
"""

# Получить расписание группы
SELECT_GROUP_SCHEDULE = """
    SELECT *
    FROM schedules
    WHERE group_id = %(group_id)s AND is_active = true
        AND (%(day_of_week)s IS NULL OR day_of_week = %(day_of_week)s)
    ORDER BY day_of_week, time_slot
"""

# Получить занятые слоты для преподавателя
SELECT_TEACHER_BUSY_SLOTS = """
    SELECT day_of_week, time_slot
    FROM schedules
    WHERE teacher_id = %(teacher_id)s 
        AND generation_id = %(generation_id)s
    ORDER BY day_of_week, time_slot
"""

# Получить занятые слоты для группы
SELECT_GROUP_BUSY_SLOTS = """
    SELECT day_of_week, time_slot
    FROM schedules
    WHERE group_id = %(group_id)s 
        AND generation_id = %(generation_id)s
    ORDER BY day_of_week, time_slot
"""

# Проверить конфликты
CHECK_CONFLICTS = """
    SELECT 
        'teacher' as conflict_type, teacher_id as entity_id, 
        day_of_week, time_slot, COUNT(*) as count
    FROM schedules
    WHERE generation_id = %(generation_id)s
    GROUP BY teacher_id, day_of_week, time_slot
    HAVING COUNT(*) > 1
    
    UNION ALL
    
    SELECT 
        'group' as conflict_type, group_id as entity_id,
        day_of_week, time_slot, COUNT(*) as count
    FROM schedules
    WHERE generation_id = %(generation_id)s
    GROUP BY group_id, day_of_week, time_slot
    HAVING COUNT(*) > 1
    
    UNION ALL
    
    SELECT 
        'classroom' as conflict_type, classroom_id as entity_id,
        day_of_week, time_slot, COUNT(*) as count
    FROM schedules
    WHERE generation_id = %(generation_id)s AND classroom_id IS NOT NULL
    GROUP BY classroom_id, day_of_week, time_slot
    HAVING COUNT(*) > 1
"""

# Деактивировать старые расписания
DEACTIVATE_OLD_SCHEDULES = """
    UPDATE schedules
    SET is_active = false
    WHERE is_active = true
"""

# Активировать расписание по generation_id
ACTIVATE_SCHEDULE_BY_GENERATION = """
    UPDATE schedules
    SET is_active = true
    WHERE generation_id = %(generation_id)s
"""

# Удалить расписание по generation_id
DELETE_SCHEDULES_BY_GENERATION = """
    DELETE FROM schedules
    WHERE generation_id = %(generation_id)s
"""

# Подсчет занятий по дням недели
COUNT_LESSONS_BY_DAY = """
    SELECT 
        day_of_week,
        COUNT(*) as lesson_count
    FROM schedules
    WHERE generation_id = %(generation_id)s
    GROUP BY day_of_week
    ORDER BY day_of_week
"""

# Подсчет занятий по временным слотам
COUNT_LESSONS_BY_TIME_SLOT = """
    SELECT 
        time_slot,
        COUNT(*) as lesson_count
    FROM schedules
    WHERE generation_id = %(generation_id)s
    GROUP BY time_slot
    ORDER BY time_slot
"""

# Получить загрузку преподавателя
SELECT_TEACHER_WORKLOAD = """
    SELECT 
        teacher_id, teacher_name,
        day_of_week,
        COUNT(*) as lessons_count,
        STRING_AGG(time_slot::text, ',' ORDER BY time_slot) as time_slots
    FROM schedules
    WHERE generation_id = %(generation_id)s
    GROUP BY teacher_id, teacher_name, day_of_week
    ORDER BY teacher_name, day_of_week
"""

# Bulk insert для начального расписания
BULK_INSERT_SCHEDULES = """
    INSERT INTO schedules (
        course_load_id, day_of_week, time_slot,
        classroom_id, classroom_name,
        teacher_id, teacher_name, group_id, group_name,
        discipline_name, lesson_type, generation_id, is_active,
        semester, academic_year
    )
    SELECT 
        unnest(%(course_load_ids)s::int[]),
        unnest(%(days)s::int[]),
        unnest(%(slots)s::int[]),
        unnest(%(classroom_ids)s::int[]),
        unnest(%(classroom_names)s::text[]),
        unnest(%(teacher_ids)s::int[]),
        unnest(%(teacher_names)s::text[]),
        unnest(%(group_ids)s::int[]),
        unnest(%(group_names)s::text[]),
        unnest(%(discipline_names)s::text[]),
        unnest(%(lesson_types)s::text[]),
        %(generation_id)s,
        %(is_active)s,
        %(semester)s,
        %(academic_year)s
"""

