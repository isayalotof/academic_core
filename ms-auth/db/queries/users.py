"""
SQL Queries for Users
Все SQL запросы для работы с пользователями
"""

# ============ INSERT ============

INSERT_USER = """
    INSERT INTO users (
        username, email, password_hash, full_name, phone,
        primary_role, teacher_id, student_group_id, is_active
    ) VALUES (
        %(username)s, %(email)s, %(password_hash)s, %(full_name)s, %(phone)s,
        %(primary_role)s, %(teacher_id)s, %(student_group_id)s, true
    )
    RETURNING id, created_at
"""

# ============ SELECT ============

SELECT_USER_BY_ID = """
    SELECT 
        u.*,
        ARRAY_AGG(DISTINCT r.code) FILTER (WHERE r.code IS NOT NULL) as roles
    FROM users u
    LEFT JOIN user_roles ur ON u.id = ur.user_id
    LEFT JOIN roles r ON ur.role_id = r.id
    WHERE u.id = %(id)s
    GROUP BY u.id
"""

SELECT_USER_BY_USERNAME = """
    SELECT 
        u.*,
        ARRAY_AGG(DISTINCT r.code) FILTER (WHERE r.code IS NOT NULL) as roles
    FROM users u
    LEFT JOIN user_roles ur ON u.id = ur.user_id
    LEFT JOIN roles r ON ur.role_id = r.id
    WHERE u.username = %(username)s
    GROUP BY u.id
"""

SELECT_USER_BY_EMAIL = """
    SELECT 
        u.*,
        ARRAY_AGG(DISTINCT r.code) FILTER (WHERE r.code IS NOT NULL) as roles
    FROM users u
    LEFT JOIN user_roles ur ON u.id = ur.user_id
    LEFT JOIN roles r ON ur.role_id = r.id
    WHERE u.email = %(email)s
    GROUP BY u.id
"""

CHECK_USER_EXISTS = """
    SELECT 
        EXISTS(SELECT 1 FROM users WHERE username = %(username)s) as username_exists,
        EXISTS(SELECT 1 FROM users WHERE email = %(email)s) as email_exists
"""

# ============ UPDATE ============

UPDATE_USER = """
    UPDATE users 
    SET 
        full_name = COALESCE(%(full_name)s, full_name),
        email = COALESCE(%(email)s, email),
        phone = COALESCE(%(phone)s, phone),
        is_active = COALESCE(%(is_active)s, is_active),
        updated_at = NOW()
    WHERE id = %(id)s
    RETURNING *
"""

UPDATE_PASSWORD = """
    UPDATE users 
    SET password_hash = %(password_hash)s, updated_at = NOW()
    WHERE id = %(id)s
"""

INCREMENT_FAILED_ATTEMPTS = """
    UPDATE users 
    SET 
        failed_login_attempts = failed_login_attempts + 1,
        locked_until = CASE 
            WHEN failed_login_attempts + 1 >= %(max_attempts)s 
            THEN NOW() + INTERVAL '%(lockout_minutes)s minutes'
            ELSE locked_until
        END
    WHERE id = %(user_id)s
"""

RESET_FAILED_ATTEMPTS = """
    UPDATE users 
    SET 
        failed_login_attempts = 0,
        locked_until = NULL,
        last_login_at = NOW(),
        last_login_ip = %(ip_address)s
    WHERE id = %(user_id)s
"""

CHECK_USER_LOCKED = """
    SELECT 
        id,
        failed_login_attempts >= %(max_attempts)s as is_locked,
        locked_until > NOW() as is_currently_locked,
        locked_until
    FROM users
    WHERE id = %(user_id)s
"""

# ============ DELETE ============

DELETE_USER_SOFT = """
    UPDATE users 
    SET is_active = false, updated_at = NOW()
    WHERE id = %(id)s
"""

DELETE_USER_HARD = """
    DELETE FROM users WHERE id = %(id)s
"""

# ============ LIST ============

LIST_USERS = """
    SELECT 
        u.*,
        ARRAY_AGG(DISTINCT r.code) FILTER (WHERE r.code IS NOT NULL) as roles
    FROM users u
    LEFT JOIN user_roles ur ON u.id = ur.user_id
    LEFT JOIN roles r ON ur.role_id = r.id
    WHERE 
        (%(only_active)s IS NULL OR u.is_active = %(only_active)s)
        AND (%(search_query)s IS NULL OR 
             u.username ILIKE %(search_pattern)s OR 
             u.email ILIKE %(search_pattern)s OR 
             u.full_name ILIKE %(search_pattern)s)
    GROUP BY u.id
    ORDER BY 
        CASE 
            WHEN %(sort_by)s = 'username' THEN u.username
            WHEN %(sort_by)s = 'email' THEN u.email
            WHEN %(sort_by)s = 'created_at' THEN u.created_at::text
            ELSE u.id::text
        END %(sort_order)s
    LIMIT %(page_size)s OFFSET %(offset)s
"""

COUNT_USERS = """
    SELECT COUNT(*) as total
    FROM users u
    WHERE 
        (%(only_active)s IS NULL OR u.is_active = %(only_active)s)
        AND (%(search_query)s IS NULL OR 
             u.username ILIKE %(search_pattern)s OR 
             u.email ILIKE %(search_pattern)s OR 
             u.full_name ILIKE %(search_pattern)s)
"""

