"""
⭐ SQL queries for teacher_preferences table
KEY FEATURE для LLM-агента!
"""

# ============ READ ============

GET_PREFERENCES_BY_TEACHER = """
SELECT 
    id, teacher_id,
    day_of_week, time_slot,
    is_preferred, preference_strength, reason,
    created_at, updated_at
FROM teacher_preferences
WHERE teacher_id = %(teacher_id)s
ORDER BY day_of_week, time_slot;
"""

GET_PREFERENCES_WITH_TEACHER_INFO = """
SELECT 
    t.id as teacher_id,
    t.full_name as teacher_name,
    t.priority as teacher_priority,
    tp.id, tp.day_of_week, tp.time_slot,
    tp.is_preferred, tp.preference_strength, tp.reason,
    tp.created_at, tp.updated_at
FROM teachers t
LEFT JOIN teacher_preferences tp ON tp.teacher_id = t.id
WHERE t.id = %(teacher_id)s
ORDER BY tp.day_of_week, tp.time_slot;
"""

# ⭐ КЛЮЧЕВОЙ ЗАПРОС ДЛЯ MS-AGENT
# Получить ВСЕ предпочтения преподавателей для fitness-функции
GET_ALL_PREFERENCES = """
SELECT 
    t.id as teacher_id,
    t.full_name as teacher_name,
    t.priority as teacher_priority,
    t.employment_type,
    tp.id as preference_id,
    tp.day_of_week,
    tp.time_slot,
    tp.is_preferred,
    tp.preference_strength
FROM teachers t
LEFT JOIN teacher_preferences tp ON tp.teacher_id = t.id
WHERE t.is_active = true
    {filters}
ORDER BY t.id, tp.day_of_week, tp.time_slot;
"""

# Статистика предпочтений
GET_PREFERENCES_STATS = """
SELECT 
    teacher_id,
    COUNT(*) as total_preferences,
    COUNT(*) FILTER (WHERE is_preferred = true) as preferred_count,
    COUNT(*) FILTER (WHERE is_preferred = false) as not_preferred_count,
    ROUND((COUNT(*)::DECIMAL / 36 * 100), 2) as coverage_percentage
FROM teacher_preferences
WHERE teacher_id = %(teacher_id)s
GROUP BY teacher_id;
"""

# ============ CREATE/UPDATE ============

UPSERT_PREFERENCE = """
INSERT INTO teacher_preferences (
    teacher_id, day_of_week, time_slot,
    is_preferred, preference_strength, reason
)
VALUES (
    %(teacher_id)s, %(day_of_week)s, %(time_slot)s,
    %(is_preferred)s, %(preference_strength)s, %(reason)s
)
ON CONFLICT (teacher_id, day_of_week, time_slot)
DO UPDATE SET
    is_preferred = EXCLUDED.is_preferred,
    preference_strength = EXCLUDED.preference_strength,
    reason = EXCLUDED.reason,
    updated_at = NOW()
RETURNING id, teacher_id, day_of_week, time_slot, is_preferred;
"""

BATCH_INSERT_PREFERENCES = """
INSERT INTO teacher_preferences (
    teacher_id, day_of_week, time_slot,
    is_preferred, preference_strength, reason
)
VALUES %s
ON CONFLICT (teacher_id, day_of_week, time_slot)
DO UPDATE SET
    is_preferred = EXCLUDED.is_preferred,
    preference_strength = EXCLUDED.preference_strength,
    reason = EXCLUDED.reason,
    updated_at = NOW();
"""

# ============ DELETE ============

DELETE_PREFERENCES_BY_TEACHER = """
DELETE FROM teacher_preferences
WHERE teacher_id = %(teacher_id)s
RETURNING id;
"""

DELETE_SINGLE_PREFERENCE = """
DELETE FROM teacher_preferences
WHERE teacher_id = %(teacher_id)s
    AND day_of_week = %(day_of_week)s
    AND time_slot = %(time_slot)s
RETURNING id;
"""

# ============ HELPER FUNCTIONS ============

def build_preferences_filters(
    teacher_ids: list = None,
    semester: int = None,
    academic_year: str = None
) -> str:
    """Построить фильтры для GET_ALL_PREFERENCES"""
    filters = []
    
    if teacher_ids:
        ids_str = ', '.join(map(str, teacher_ids))
        filters.append(f"AND t.id IN ({ids_str})")
    
    # Здесь можно добавить фильтры по семестру/году если нужно
    # (например, если предпочтения могут меняться от семестра к семестру)
    
    return ' '.join(filters) if filters else ''

