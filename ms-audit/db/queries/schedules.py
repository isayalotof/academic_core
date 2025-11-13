"""
SQL Queries for Classroom Schedules
Все SQL запросы для работы с расписанием аудиторий
"""

# ============ INSERT ============

INSERT_SCHEDULE = """
    INSERT INTO classroom_schedules (
        classroom_id, day_of_week, time_slot, week, schedule_id,
        discipline_name, teacher_name, group_name, lesson_type, status
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    ) RETURNING id, created_at
"""

# ============ SELECT ============

SELECT_SCHEDULE_BY_ID = """
    SELECT * FROM classroom_schedules WHERE id = %s
"""

SELECT_CLASSROOM_SCHEDULE = """
    SELECT 
        cs.*,
        c.name as classroom_name,
        c.code as classroom_code
    FROM classroom_schedules cs
    LEFT JOIN classrooms c ON cs.classroom_id = c.id
    WHERE cs.classroom_id = %s
    AND (%s IS NULL OR cs.day_of_week = ANY(%s))
    AND (%s IS NULL OR cs.week = %s OR (cs.week IS NULL AND %s IS NULL))
    ORDER BY COALESCE(cs.week, 0), cs.day_of_week, cs.time_slot
"""

SELECT_SCHEDULE_BY_TIME_SLOT = """
    SELECT 
        cs.*,
        c.name as classroom_name,
        c.code as classroom_code,
        b.name as building_name
    FROM classroom_schedules cs
    LEFT JOIN classrooms c ON cs.classroom_id = c.id
    LEFT JOIN buildings b ON c.building_id = b.id
    WHERE cs.day_of_week = %s AND cs.time_slot = %s
    ORDER BY b.name, c.name
"""

# ============ DELETE ============

DELETE_SCHEDULE = """
    DELETE FROM classroom_schedules WHERE id = %s
"""

DELETE_SCHEDULE_BY_SLOT = """
    DELETE FROM classroom_schedules 
    WHERE classroom_id = %s 
    AND day_of_week = %s 
    AND time_slot = %s
"""

DELETE_ALL_CLASSROOM_SCHEDULES = """
    DELETE FROM classroom_schedules WHERE classroom_id = %s
"""

# ============ UPDATE ============

UPDATE_SCHEDULE_STATUS = """
    UPDATE classroom_schedules 
    SET status = %s
    WHERE id = %s
"""

# ============ BULK OPERATIONS ============

BULK_INSERT_SCHEDULES = """
    INSERT INTO classroom_schedules (
        classroom_id, day_of_week, time_slot, week, schedule_id,
        discipline_name, teacher_name, group_name, lesson_type, status
    ) VALUES %s
    ON CONFLICT (classroom_id, day_of_week, time_slot, week) DO NOTHING
    RETURNING id
"""

# ============ STATISTICS ============

GET_SCHEDULE_UTILIZATION = """
    SELECT 
        cs.classroom_id,
        COUNT(*) as occupied_slots,
        ROUND((COUNT(*)::DECIMAL / 36) * 100, 2) as utilization_percentage
    FROM classroom_schedules cs
    WHERE cs.classroom_id = %s
    GROUP BY cs.classroom_id
"""

GET_WEEKLY_SCHEDULE = """
    SELECT 
        day_of_week,
        time_slot,
        COUNT(*) as occupied_classrooms
    FROM classroom_schedules
    GROUP BY day_of_week, time_slot
    ORDER BY day_of_week, time_slot
"""

