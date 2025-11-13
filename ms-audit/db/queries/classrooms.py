"""
SQL Queries for Classrooms
Все SQL запросы для работы с аудиториями
"""

# ============ INSERT ============

INSERT_CLASSROOM = """
    INSERT INTO classrooms (
        name, code, building_id, floor, wing, capacity, actual_area,
        classroom_type, has_projector, has_whiteboard, has_blackboard,
        has_markers, has_chalk, has_computers, computers_count,
        has_audio_system, has_video_recording, has_air_conditioning,
        is_accessible, has_windows, description, created_by
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    ) RETURNING id, created_at
"""

# ============ SELECT ============

SELECT_CLASSROOM_BY_ID = """
    SELECT 
        c.*,
        b.name as building_name,
        b.short_name as building_short_name,
        b.code as building_code
    FROM classrooms c
    LEFT JOIN buildings b ON c.building_id = b.id
    WHERE c.id = %s
"""

SELECT_CLASSROOM_BY_CODE = """
    SELECT 
        c.*,
        b.name as building_name,
        b.short_name as building_short_name,
        b.code as building_code
    FROM classrooms c
    LEFT JOIN buildings b ON c.building_id = b.id
    WHERE c.code = %s
"""

SELECT_ALL_CLASSROOMS = """
    SELECT 
        c.*,
        b.name as building_name
    FROM classrooms c
    LEFT JOIN buildings b ON c.building_id = b.id
    WHERE c.is_active = true
    ORDER BY c.name
"""

# ============ UPDATE ============

UPDATE_CLASSROOM = """
    UPDATE classrooms 
    SET {updates}
    WHERE id = %s
    RETURNING id, updated_at
"""

UPDATE_CLASSROOM_STATUS = """
    UPDATE classrooms 
    SET is_active = %s, updated_by = %s
    WHERE id = %s
"""

# ============ DELETE ============

DELETE_CLASSROOM_SOFT = """
    UPDATE classrooms 
    SET is_active = false, updated_by = %s
    WHERE id = %s
"""

DELETE_CLASSROOM_HARD = """
    DELETE FROM classrooms 
    WHERE id = %s
"""

# ============ SEARCH ============

SEARCH_CLASSROOMS = """
    SELECT 
        c.*,
        b.name as building_name
    FROM classrooms c
    LEFT JOIN buildings b ON c.building_id = b.id
    WHERE 
        c.is_active = true
        AND (
            %s IS NULL OR 
            c.name ILIKE %s OR 
            c.code ILIKE %s OR 
            b.name ILIKE %s
        )
        AND (%s IS NULL OR c.building_id = ANY(%s))
        AND (%s IS NULL OR c.classroom_type = ANY(%s))
        AND (%s IS NULL OR c.capacity >= %s)
        AND (%s IS NULL OR c.capacity <= %s)
    ORDER BY 
        CASE 
            WHEN %s = 'name' THEN c.name
            WHEN %s = 'capacity' THEN c.capacity::text
            WHEN %s = 'building' THEN b.name
            ELSE c.id::text
        END {order}
    LIMIT %s OFFSET %s
"""

COUNT_CLASSROOMS = """
    SELECT COUNT(*) as total
    FROM classrooms c
    LEFT JOIN buildings b ON c.building_id = b.id
    WHERE 
        c.is_active = true
        AND (
            %s IS NULL OR 
            c.name ILIKE %s OR 
            c.code ILIKE %s OR 
            b.name ILIKE %s
        )
        AND (%s IS NULL OR c.building_id = ANY(%s))
        AND (%s IS NULL OR c.classroom_type = ANY(%s))
        AND (%s IS NULL OR c.capacity >= %s)
        AND (%s IS NULL OR c.capacity <= %s)
"""

# ============ AVAILABILITY ============

FIND_AVAILABLE_CLASSROOMS = """
    SELECT * FROM (
        SELECT 
            c.*,
            b.name as building_name,
            (SELECT COUNT(*) FROM classroom_schedules cs 
             WHERE cs.classroom_id = c.id) as total_scheduled_slots
        FROM classrooms c
        LEFT JOIN buildings b ON c.building_id = b.id
        WHERE 
            c.is_active = true
            AND c.capacity >= %s
            AND (%s = false OR c.has_projector = true)
            AND (%s = false OR c.has_whiteboard = true)
            AND (%s = false OR c.has_computers = true)
            AND (%s IS NULL OR c.building_id = ANY(%s))
            AND (%s IS NULL OR c.classroom_type = ANY(%s))
            AND c.id NOT IN (
                SELECT classroom_id 
                FROM classroom_schedules 
                WHERE day_of_week = %s AND time_slot = %s
            )
    ) subquery
    ORDER BY 
        CASE 
            WHEN %s = 'capacity' THEN capacity
            WHEN %s = 'utilization' THEN total_scheduled_slots
            ELSE id
        END {order}
    LIMIT 50
"""

CHECK_AVAILABILITY = """
    SELECT NOT EXISTS (
        SELECT 1 
        FROM classroom_schedules 
        WHERE classroom_id = %s 
        AND day_of_week = %s 
        AND time_slot = %s
        AND (%s IS NULL OR week = %s)
    ) as is_available
"""

# ============ STATISTICS ============

GET_CLASSROOM_UTILIZATION = """
    SELECT 
        c.id,
        c.name,
        COUNT(cs.id) as occupied_slots,
        ROUND((COUNT(cs.id)::DECIMAL / 36) * 100, 2) as utilization_percentage
    FROM classrooms c
    LEFT JOIN classroom_schedules cs ON c.classroom_id = cs.classroom_id
    WHERE c.id = %s
    GROUP BY c.id, c.name
"""

GET_BUILDING_STATISTICS = """
    SELECT 
        b.id,
        b.name,
        COUNT(DISTINCT c.id) as total_classrooms,
        COALESCE(SUM(c.capacity), 0)::INTEGER as total_capacity,
        COALESCE(AVG(c.capacity), 0) as avg_capacity,
        COUNT(cs.id) as total_occupied_slots
    FROM buildings b
    LEFT JOIN classrooms c ON b.id = c.building_id AND c.is_active = true
    LEFT JOIN classroom_schedules cs ON c.id = cs.classroom_id
    WHERE (%s IS NULL OR b.id = %s)
    GROUP BY b.id, b.name
"""

GET_OVERALL_STATISTICS = """
    SELECT 
        COUNT(DISTINCT c.id) as total_classrooms,
        SUM(c.capacity) as total_capacity,
        COUNT(cs.id) as total_occupied_slots,
        ROUND((COUNT(cs.id)::DECIMAL / (COUNT(DISTINCT c.id) * 36)) * 100, 2) as avg_utilization
    FROM classrooms c
    LEFT JOIN classroom_schedules cs ON c.id = cs.classroom_id
    WHERE c.is_active = true
"""

GET_STATISTICS_BY_TYPE = """
    SELECT 
        c.classroom_type,
        COUNT(*) as count
    FROM classrooms c
    WHERE c.is_active = true
    GROUP BY c.classroom_type
"""

