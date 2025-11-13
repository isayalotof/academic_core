"""
SQL запросы для истории генераций
"""

# Создать запись о генерации
INSERT_GENERATION = """
    INSERT INTO generation_history (
        job_id, stage, stage_name, status,
        max_iterations, initial_score, created_by
    ) VALUES (
        %(job_id)s, %(stage)s, %(stage_name)s, %(status)s,
        %(max_iterations)s, %(initial_score)s, %(created_by)s
    )
    RETURNING id
"""

# Обновить статус генерации
UPDATE_GENERATION_STATUS = """
    UPDATE generation_history
    SET status = %(status)s,
        completed_at = CASE WHEN %(status)s IN ('completed', 'failed', 'stopped') 
                             THEN NOW() ELSE completed_at END,
        duration_seconds = CASE WHEN %(status)s IN ('completed', 'failed', 'stopped')
                                THEN EXTRACT(EPOCH FROM (NOW() - started_at))::int 
                                ELSE duration_seconds END,
        error_message = %(error_message)s
    WHERE job_id = %(job_id)s
"""

# Обновить итерацию и скор
UPDATE_GENERATION_ITERATION = """
    UPDATE generation_history
    SET current_iteration = %(current_iteration)s,
        current_score = %(current_score)s,
        best_score = CASE 
            WHEN %(current_score)s > COALESCE(best_score, -999999) 
            THEN %(current_score)s 
            ELSE best_score 
        END,
        last_reasoning = %(last_reasoning)s,
        total_actions = total_actions + 1
    WHERE job_id = %(job_id)s
"""

# Обновить метрики
UPDATE_GENERATION_METRICS = """
    UPDATE generation_history
    SET metrics = %(metrics)s
    WHERE job_id = %(job_id)s
"""

# Получить генерацию по job_id
SELECT_GENERATION_BY_JOB_ID = """
    SELECT *
    FROM generation_history
    WHERE job_id = %(job_id)s
"""

# Получить генерацию по ID
SELECT_GENERATION_BY_ID = """
    SELECT *
    FROM generation_history
    WHERE id = %(id)s
"""

# Получить последнюю генерацию
SELECT_LAST_GENERATION = """
    SELECT *
    FROM generation_history
    ORDER BY started_at DESC
    LIMIT 1
"""

# Получить активные генерации
SELECT_ACTIVE_GENERATIONS = """
    SELECT *
    FROM generation_history
    WHERE status = 'running'
    ORDER BY started_at DESC
"""

# Получить историю генераций
SELECT_GENERATION_HISTORY = """
    SELECT *
    FROM generation_history
    WHERE (%(status)s IS NULL OR status = %(status)s)
        AND (%(stage)s IS NULL OR stage = %(stage)s)
    ORDER BY started_at DESC
    LIMIT %(limit)s OFFSET %(offset)s
"""

# Получить статистику по генерациям
SELECT_GENERATION_STATISTICS = """
    SELECT 
        stage,
        status,
        COUNT(*) as count,
        AVG(duration_seconds) as avg_duration,
        AVG(best_score) as avg_best_score,
        AVG(total_actions) as avg_actions
    FROM generation_history
    WHERE completed_at IS NOT NULL
    GROUP BY stage, status
    ORDER BY stage, status
"""

