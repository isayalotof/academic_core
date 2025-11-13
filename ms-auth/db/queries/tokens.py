"""
SQL Queries for Refresh Tokens
Все SQL запросы для работы с refresh токенами
"""

# ============ INSERT ============

INSERT_REFRESH_TOKEN = """
    INSERT INTO refresh_tokens (
        user_id, token, token_family, expires_at,
        ip_address, user_agent, device_id
    ) VALUES (
        %(user_id)s, %(token)s, %(token_family)s, %(expires_at)s,
        %(ip_address)s, %(user_agent)s, %(device_id)s
    )
    RETURNING id
"""

# ============ SELECT ============

SELECT_REFRESH_TOKEN = """
    SELECT * FROM refresh_tokens
    WHERE token = %(token)s 
      AND is_active = true
      AND expires_at > NOW()
"""

SELECT_ACTIVE_TOKENS = """
    SELECT * FROM refresh_tokens
    WHERE user_id = %(user_id)s
      AND is_active = true
      AND expires_at > NOW()
    ORDER BY created_at DESC
"""

# ============ UPDATE ============

MARK_TOKEN_USED = """
    UPDATE refresh_tokens
    SET used_at = NOW()
    WHERE id = %(token_id)s
"""

REVOKE_REFRESH_TOKEN = """
    UPDATE refresh_tokens
    SET is_active = false, revoked_at = NOW()
    WHERE token = %(token)s
"""

REVOKE_USER_TOKENS = """
    UPDATE refresh_tokens
    SET is_active = false, revoked_at = NOW()
    WHERE user_id = %(user_id)s AND is_active = true
"""

REVOKE_TOKEN_FAMILY = """
    UPDATE refresh_tokens
    SET is_active = false, revoked_at = NOW()
    WHERE token_family = %(token_family)s AND is_active = true
"""

# ============ DELETE ============

DELETE_EXPIRED_TOKENS = """
    DELETE FROM refresh_tokens
    WHERE expires_at < NOW()
"""

# ============ PASSWORD RESET TOKENS ============

INSERT_PASSWORD_RESET_TOKEN = """
    INSERT INTO password_reset_tokens (
        user_id, token, expires_at, ip_address
    ) VALUES (
        %(user_id)s, %(token)s, %(expires_at)s, %(ip_address)s
    )
    RETURNING id
"""

SELECT_PASSWORD_RESET_TOKEN = """
    SELECT * FROM password_reset_tokens
    WHERE token = %(token)s
      AND used_at IS NULL
      AND expires_at > NOW()
"""

MARK_PASSWORD_RESET_USED = """
    UPDATE password_reset_tokens
    SET used_at = NOW()
    WHERE token = %(token)s
"""

DELETE_USER_PASSWORD_RESET_TOKENS = """
    DELETE FROM password_reset_tokens
    WHERE user_id = %(user_id)s
"""

