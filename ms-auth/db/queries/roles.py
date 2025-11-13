"""
SQL Queries for Roles
Все SQL запросы для работы с ролями
"""

# ============ SELECT ============

SELECT_ROLE_BY_ID = """
    SELECT * FROM roles WHERE id = %(id)s
"""

SELECT_ROLE_BY_CODE = """
    SELECT * FROM roles WHERE code = %(code)s
"""

SELECT_ALL_ROLES = """
    SELECT * FROM roles ORDER BY name
"""

# ============ USER ROLES ============

INSERT_USER_ROLE = """
    INSERT INTO user_roles (user_id, role_id, granted_by)
    VALUES (%(user_id)s, %(role_id)s, %(granted_by)s)
    ON CONFLICT (user_id, role_id) DO NOTHING
"""

DELETE_USER_ROLE = """
    DELETE FROM user_roles
    WHERE user_id = %(user_id)s AND role_id = %(role_id)s
"""

SELECT_USER_ROLES = """
    SELECT r.*
    FROM roles r
    INNER JOIN user_roles ur ON r.id = ur.role_id
    WHERE ur.user_id = %(user_id)s
"""

CHECK_USER_HAS_ROLE = """
    SELECT EXISTS(
        SELECT 1 FROM user_roles
        WHERE user_id = %(user_id)s AND role_id = %(role_id)s
    ) as has_role
"""

