"""
SQL Queries for Classroom Distances
Все SQL запросы для работы с расстояниями между аудиториями
"""

# ============ INSERT ============

INSERT_DISTANCE = """
    INSERT INTO classroom_distances (
        from_classroom_id, to_classroom_id, distance_meters,
        walking_time_seconds, requires_building_change, requires_floor_change
    ) VALUES (
        %s, %s, %s, %s, %s, %s
    ) 
    ON CONFLICT (from_classroom_id, to_classroom_id) 
    DO UPDATE SET
        distance_meters = EXCLUDED.distance_meters,
        walking_time_seconds = EXCLUDED.walking_time_seconds,
        requires_building_change = EXCLUDED.requires_building_change,
        requires_floor_change = EXCLUDED.requires_floor_change,
        calculated_at = NOW()
    RETURNING id
"""

# ============ SELECT ============

SELECT_DISTANCE = """
    SELECT * 
    FROM classroom_distances 
    WHERE from_classroom_id = %s AND to_classroom_id = %s
"""

SELECT_DISTANCES_FROM_CLASSROOM = """
    SELECT 
        cd.*,
        c.name as to_classroom_name,
        c.code as to_classroom_code
    FROM classroom_distances cd
    LEFT JOIN classrooms c ON cd.to_classroom_id = c.id
    WHERE cd.from_classroom_id = %s
    ORDER BY cd.distance_meters
"""

# ============ CALCULATE ============

CALCULATE_DISTANCE_QUERY = """
    SELECT 
        c1.id as from_id,
        c2.id as to_id,
        c1.building_id as from_building,
        c2.building_id as to_building,
        c1.floor as from_floor,
        c2.floor as to_floor,
        b1.latitude as from_lat,
        b1.longitude as from_lng,
        b2.latitude as to_lat,
        b2.longitude as to_lng
    FROM classrooms c1
    CROSS JOIN classrooms c2
    LEFT JOIN buildings b1 ON c1.building_id = b1.id
    LEFT JOIN buildings b2 ON c2.building_id = b2.id
    WHERE c1.id = %s AND c2.id = %s AND c1.id != c2.id
"""

# ============ DELETE ============

DELETE_DISTANCE = """
    DELETE FROM classroom_distances 
    WHERE from_classroom_id = %s AND to_classroom_id = %s
"""

DELETE_CLASSROOM_DISTANCES = """
    DELETE FROM classroom_distances 
    WHERE from_classroom_id = %s OR to_classroom_id = %s
"""

# ============ UTILITIES ============

COUNT_DISTANCES = """
    SELECT COUNT(*) as total FROM classroom_distances
"""

