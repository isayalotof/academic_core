"""
SQL Queries for Buildings
Все SQL запросы для работы со зданиями
"""

# ============ INSERT ============

INSERT_BUILDING = """
    INSERT INTO buildings (
        name, short_name, code, address, campus,
        latitude, longitude, total_floors, has_elevator
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s
    ) RETURNING id, created_at
"""

# ============ SELECT ============

SELECT_BUILDING_BY_ID = """
    SELECT * FROM buildings WHERE id = %s
"""

SELECT_BUILDING_BY_CODE = """
    SELECT * FROM buildings WHERE code = %s
"""

SELECT_ALL_BUILDINGS = """
    SELECT * FROM buildings ORDER BY name
"""

# ============ UPDATE ============

UPDATE_BUILDING = """
    UPDATE buildings 
    SET {updates}
    WHERE id = %s
    RETURNING id, updated_at
"""

# ============ DELETE ============

DELETE_BUILDING = """
    DELETE FROM buildings WHERE id = %s
"""

# ============ UTILITIES ============

COUNT_CLASSROOMS_IN_BUILDING = """
    SELECT COUNT(*) as count
    FROM classrooms
    WHERE building_id = %s AND is_active = true
"""

