"""
Authentication Middleware
JWT аутентификация для Gateway через ms-auth
"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Получить текущего пользователя из токена через ms-auth
    
    Args:
        credentials: HTTP credentials с токеном
        
    Returns:
        Данные пользователя
        
    Raises:
        HTTPException: Если токен невалиден или отсутствует
    """
    from rpc_clients.auth_client import auth_client
    
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Валидировать токен через ms-auth
    result = auth_client.validate_token(token)
    
    if not result['valid']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Вернуть информацию о пользователе
    return {
        'user_id': result['user_id'],
        'username': result['username'],
        'role': result['primary_role'],
        'roles': result['roles']
    }


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[Dict[str, Any]]:
    """
    Получить текущего пользователя (опционально)
    
    Returns:
        Данные пользователя или None
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_role(allowed_roles: list):
    """
    Декоратор для проверки роли пользователя
    
    Args:
        allowed_roles: Список разрешенных ролей
        
    Returns:
        Функция проверки роли
    """
    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        user_role = current_user.get('role')
        user_roles = current_user.get('roles', [])
        
        # Проверить основную роль или дополнительные роли
        if user_role not in allowed_roles and not any(r in allowed_roles for r in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        
        return current_user
    
    return role_checker


# Role-specific dependencies
require_admin = require_role(['admin'])
require_staff = require_role(['admin', 'staff'])
require_teacher = require_role(['admin', 'staff', 'teacher'])

