"""
SQL запросы для предпочтений преподавателей
"""

# Вставить предпочтение
INSERT_PREFERENCE = """
    INSERT INTO teacher_preferences (
        teacher_id, day_of_week, time_slot, is_preferred, preference_strength
    ) VALUES (
        %(teacher_id)s, %(day_of_week)s, %(time_slot)s, 
        %(is_preferred)s, %(preference_strength)s
    )
    ON CONFLICT (teacher_id, day_of_week, time_slot)
    DO UPDATE SET 
        is_preferred = EXCLUDED.is_preferred,
        preference_strength = EXCLUDED.preference_strength
"""

# Получить предпочтения преподавателя
SELECT_TEACHER_PREFERENCES = """
    SELECT *
    FROM teacher_preferences
    WHERE teacher_id = %(teacher_id)s
    ORDER BY day_of_week, time_slot
"""

# Получить предпочтительные слоты
SELECT_PREFERRED_SLOTS = """
    SELECT day_of_week, time_slot, preference_strength
    FROM teacher_preferences
    WHERE teacher_id = %(teacher_id)s AND is_preferred = true
    ORDER BY 
        CASE preference_strength 
            WHEN 'strong' THEN 1 
            WHEN 'medium' THEN 2 
            WHEN 'weak' THEN 3 
            ELSE 4 
        END,
        day_of_week, time_slot
"""

# Получить неудобные слоты
SELECT_NON_PREFERRED_SLOTS = """
    SELECT day_of_week, time_slot, preference_strength
    FROM teacher_preferences
    WHERE teacher_id = %(teacher_id)s AND is_preferred = false
    ORDER BY 
        CASE preference_strength 
            WHEN 'strong' THEN 1 
            WHEN 'medium' THEN 2 
            WHEN 'weak' THEN 3 
            ELSE 4 
        END,
        day_of_week, time_slot
"""

# Получить все предпочтения (для кэширования)
SELECT_ALL_PREFERENCES = """
    SELECT 
        teacher_id,
        JSON_AGG(
            JSON_BUILD_OBJECT(
                'day_of_week', day_of_week,
                'time_slot', time_slot,
                'is_preferred', is_preferred,
                'preference_strength', preference_strength
            ) ORDER BY day_of_week, time_slot
        ) as preferences
    FROM teacher_preferences
    GROUP BY teacher_id
"""

# Bulk insert предпочтений
BULK_INSERT_PREFERENCES = """
    INSERT INTO teacher_preferences (
        teacher_id, day_of_week, time_slot, is_preferred, preference_strength
    )
    SELECT 
        unnest(%(teacher_ids)s::int[]),
        unnest(%(days)s::int[]),
        unnest(%(slots)s::int[]),
        unnest(%(is_preferred_arr)s::boolean[]),
        unnest(%(strengths)s::varchar[])
    ON CONFLICT (teacher_id, day_of_week, time_slot)
    DO UPDATE SET 
        is_preferred = EXCLUDED.is_preferred,
        preference_strength = EXCLUDED.preference_strength
"""

# Удалить все предпочтения преподавателя
DELETE_TEACHER_PREFERENCES = """
    DELETE FROM teacher_preferences
    WHERE teacher_id = %(teacher_id)s
"""

# Статистика по предпочтениям
SELECT_PREFERENCE_STATISTICS = """
    SELECT 
        COUNT(DISTINCT teacher_id) as teachers_with_prefs,
        SUM(CASE WHEN is_preferred THEN 1 ELSE 0 END) as preferred_slots_count,
        SUM(CASE WHEN NOT is_preferred THEN 1 ELSE 0 END) as non_preferred_slots_count
    FROM teacher_preferences
"""

