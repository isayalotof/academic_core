"""
SQL запросы для действий агента
"""

# Вставить действие
INSERT_AGENT_ACTION = """
    INSERT INTO agent_actions (
        generation_id, iteration, action_type, action_params,
        success, score_before, score_after, score_delta,
        reasoning, execution_time_ms
    ) VALUES (
        %(generation_id)s, %(iteration)s, %(action_type)s, %(action_params)s,
        %(success)s, %(score_before)s, %(score_after)s, %(score_delta)s,
        %(reasoning)s, %(execution_time_ms)s
    )
    RETURNING id
"""

# Получить действия по generation_id
SELECT_ACTIONS_BY_GENERATION = """
    SELECT *
    FROM agent_actions
    WHERE generation_id = %(generation_id)s
    ORDER BY iteration ASC, created_at ASC
    LIMIT %(limit)s
"""

# Получить последние действия
SELECT_RECENT_ACTIONS = """
    SELECT *
    FROM agent_actions
    WHERE generation_id = %(generation_id)s
    ORDER BY created_at DESC
    LIMIT %(limit)s
"""

# Получить успешные действия с улучшением скора
SELECT_SUCCESSFUL_ACTIONS = """
    SELECT *
    FROM agent_actions
    WHERE generation_id = %(generation_id)s
        AND success = true
        AND score_delta > 0
    ORDER BY score_delta DESC
    LIMIT %(limit)s
"""

# Статистика по типам действий
SELECT_ACTION_TYPE_STATISTICS = """
    SELECT 
        action_type,
        COUNT(*) as total_count,
        SUM(CASE WHEN success THEN 1 ELSE 0 END) as success_count,
        AVG(CASE WHEN success AND score_delta IS NOT NULL 
            THEN score_delta ELSE 0 END) as avg_score_delta,
        SUM(CASE WHEN score_delta > 0 THEN 1 ELSE 0 END) as improvements_count
    FROM agent_actions
    WHERE generation_id = %(generation_id)s
    GROUP BY action_type
    ORDER BY improvements_count DESC
"""

# История скоров по итерациям
SELECT_SCORE_HISTORY = """
    SELECT 
        iteration,
        MAX(score_after) as score
    FROM agent_actions
    WHERE generation_id = %(generation_id)s
        AND score_after IS NOT NULL
    GROUP BY iteration
    ORDER BY iteration ASC
"""

# Топ улучшений
SELECT_TOP_IMPROVEMENTS = """
    SELECT 
        iteration,
        action_type,
        score_delta,
        reasoning,
        action_params
    FROM agent_actions
    WHERE generation_id = %(generation_id)s
        AND score_delta IS NOT NULL
    ORDER BY score_delta DESC
    LIMIT %(limit)s
"""

# Среднее время выполнения по типам действий
SELECT_AVG_EXECUTION_TIME = """
    SELECT 
        action_type,
        AVG(execution_time_ms) as avg_time_ms,
        MIN(execution_time_ms) as min_time_ms,
        MAX(execution_time_ms) as max_time_ms
    FROM agent_actions
    WHERE generation_id = %(generation_id)s
        AND execution_time_ms IS NOT NULL
    GROUP BY action_type
    ORDER BY avg_time_ms DESC
"""

