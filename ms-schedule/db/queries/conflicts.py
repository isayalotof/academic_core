"""
SQL queries for conflict detection
Поиск и управление конфликтами расписания
"""

# ============ DETECT CONFLICTS ============

FIND_TEACHER_CONFLICTS = """
    WITH conflict_slots AS (
        SELECT 
            day_of_week,
            time_slot,
            week_type,
            teacher_id,
            teacher_name,
            COUNT(*) as conflicts_count,
            ARRAY_AGG(id) as schedule_ids
        FROM schedules
        WHERE 
            semester = %(semester)s
            AND academic_year = %(academic_year)s
            AND is_active = true
        GROUP BY day_of_week, time_slot, week_type, teacher_id, teacher_name
        HAVING COUNT(*) > 1
    )
    SELECT 
        'teacher' as conflict_type,
        cs.teacher_id as entity_id,
        cs.teacher_name as entity_name,
        cs.day_of_week,
        cs.time_slot,
        cs.week_type,
        cs.schedule_ids,
        cs.conflicts_count
    FROM conflict_slots cs
    ORDER BY cs.conflicts_count DESC, cs.day_of_week, cs.time_slot
"""

FIND_GROUP_CONFLICTS = """
    WITH conflict_slots AS (
        SELECT 
            day_of_week,
            time_slot,
            week_type,
            group_id,
            group_name,
            COUNT(*) as conflicts_count,
            ARRAY_AGG(id) as schedule_ids
        FROM schedules
        WHERE 
            semester = %(semester)s
            AND academic_year = %(academic_year)s
            AND is_active = true
        GROUP BY day_of_week, time_slot, week_type, group_id, group_name
        HAVING COUNT(*) > 1
    )
    SELECT 
        'group' as conflict_type,
        cs.group_id as entity_id,
        cs.group_name as entity_name,
        cs.day_of_week,
        cs.time_slot,
        cs.week_type,
        cs.schedule_ids,
        cs.conflicts_count
    FROM conflict_slots cs
    ORDER BY cs.conflicts_count DESC, cs.day_of_week, cs.time_slot
"""

FIND_CLASSROOM_CONFLICTS = """
    WITH conflict_slots AS (
        SELECT 
            day_of_week,
            time_slot,
            week_type,
            classroom_id,
            classroom_name,
            COUNT(*) as conflicts_count,
            ARRAY_AGG(id) as schedule_ids
        FROM schedules
        WHERE 
            semester = %(semester)s
            AND academic_year = %(academic_year)s
            AND is_active = true
            AND classroom_id IS NOT NULL
        GROUP BY day_of_week, time_slot, week_type, classroom_id, classroom_name
        HAVING COUNT(*) > 1
    )
    SELECT 
        'classroom' as conflict_type,
        cs.classroom_id as entity_id,
        cs.classroom_name as entity_name,
        cs.day_of_week,
        cs.time_slot,
        cs.week_type,
        cs.schedule_ids,
        cs.conflicts_count
    FROM conflict_slots cs
    ORDER BY cs.conflicts_count DESC, cs.day_of_week, cs.time_slot
"""

# ============ CHECK SPECIFIC LESSON ============

CHECK_LESSON_CONFLICTS = """
    SELECT 
        id,
        teacher_id,
        teacher_name,
        group_id,
        group_name,
        classroom_id,
        classroom_name,
        discipline_name
    FROM schedules
    WHERE 
        day_of_week = %(day_of_week)s
        AND time_slot = %(time_slot)s
        AND (week_type = %(week_type)s OR week_type = 'both' OR %(week_type)s = 'both')
        AND semester = %(semester)s
        AND academic_year = %(academic_year)s
        AND is_active = true
        AND (
            teacher_id = %(teacher_id)s
            OR group_id = %(group_id)s
            OR (classroom_id = %(classroom_id)s AND %(classroom_id)s IS NOT NULL)
        )
        AND id != COALESCE(%(exclude_id)s, -1)
"""

# ============ MANAGE CONFLICTS TABLE ============

INSERT_CONFLICT = """
    INSERT INTO schedule_conflicts (
        day_of_week, time_slot, week_type,
        conflict_type, entity_id, entity_name,
        schedule_ids, semester, academic_year, severity
    ) VALUES (
        %(day_of_week)s, %(time_slot)s, %(week_type)s,
        %(conflict_type)s, %(entity_id)s, %(entity_name)s,
        %(schedule_ids)s, %(semester)s, %(academic_year)s, %(severity)s
    )
    RETURNING *
"""

GET_CONFLICTS = """
    SELECT 
        c.*,
        ARRAY_LENGTH(c.schedule_ids, 1) as conflict_count
    FROM schedule_conflicts c
    WHERE 
        c.semester = %(semester)s
        AND c.academic_year = %(academic_year)s
        AND (%(status)s IS NULL OR c.status = %(status)s)
        AND (%(conflict_types)s IS NULL OR c.conflict_type = ANY(%(conflict_types)s))
    ORDER BY 
        CASE c.severity
            WHEN 'critical' THEN 1
            WHEN 'high' THEN 2
            WHEN 'medium' THEN 3
            ELSE 4
        END,
        c.detected_at DESC
"""

GET_CONFLICT_BY_ID = """
    SELECT * FROM schedule_conflicts WHERE id = %(id)s
"""

RESOLVE_CONFLICT = """
    UPDATE schedule_conflicts
    SET 
        status = 'resolved',
        resolution = %(resolution)s,
        resolved_at = NOW(),
        resolved_by = %(resolved_by)s
    WHERE id = %(id)s
    RETURNING *
"""

DELETE_RESOLVED_CONFLICTS = """
    DELETE FROM schedule_conflicts
    WHERE 
        status = 'resolved'
        AND resolved_at < NOW() - INTERVAL '30 days'
"""

# ============ COUNT CONFLICTS ============

COUNT_CONFLICTS_BY_TYPE = """
    SELECT 
        conflict_type,
        COUNT(*) as count,
        COUNT(*) FILTER (WHERE severity = 'critical') as critical_count,
        COUNT(*) FILTER (WHERE severity = 'high') as high_count
    FROM schedule_conflicts
    WHERE 
        semester = %(semester)s
        AND academic_year = %(academic_year)s
        AND status = 'active'
    GROUP BY conflict_type
"""

