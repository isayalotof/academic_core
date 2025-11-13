"""
SQL Queries for Login History
Все SQL запросы для работы с историей входов
"""

# ============ INSERT ============

INSERT_LOGIN_HISTORY = """
    INSERT INTO login_history (
        user_id, username, success, ip_address, user_agent, failure_reason
    ) VALUES (
        %(user_id)s, %(username)s, %(success)s, %(ip_address)s, %(user_agent)s, %(failure_reason)s
    )
"""

# ============ SELECT ============

GET_LOGIN_HISTORY = """
    SELECT * FROM login_history
    WHERE user_id = %(user_id)s
    AND (%(only_successful)s IS NULL OR success = %(only_successful)s)
    ORDER BY created_at DESC
    LIMIT %(limit)s
"""

GET_RECENT_FAILED_LOGINS = """
    SELECT COUNT(*) as failed_count
    FROM login_history
    WHERE user_id = %(user_id)s
      AND success = false
      AND created_at > NOW() - INTERVAL '%(minutes)s minutes'
"""

