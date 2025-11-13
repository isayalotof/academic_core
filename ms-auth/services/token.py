"""
Token Service
Сервис для создания и валидации JWT токенов
"""

import jwt
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from config import config

logger = logging.getLogger(__name__)


class TokenService:
    """Сервис для работы с JWT токенами"""
    
    def create_access_token(
        self,
        user_id: int,
        username: str,
        primary_role: str,
        roles: list
    ) -> str:
        """
        Создать access token (короткий срок жизни)
        
        Args:
            user_id: ID пользователя
            username: Имя пользователя
            primary_role: Основная роль
            roles: Список всех ролей
            
        Returns:
            JWT токен
        """
        try:
            expire = datetime.utcnow() + timedelta(
                minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )
            
            payload = {
                'sub': str(user_id),
                'username': username,
                'role': primary_role,
                'roles': roles,
                'exp': expire,
                'iat': datetime.utcnow(),
                'type': 'access'
            }
            
            token = jwt.encode(
                payload,
                config.JWT_SECRET_KEY,
                algorithm=config.JWT_ALGORITHM
            )
            
            return token
            
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise
    
    def create_refresh_token(self, user_id: int) -> str:
        """
        Создать refresh token (длинный срок жизни)
        
        Args:
            user_id: ID пользователя
            
        Returns:
            JWT токен
        """
        import uuid
        
        try:
            now = datetime.utcnow()
            expire = now + timedelta(
                days=config.JWT_REFRESH_TOKEN_EXPIRE_DAYS
            )
            
            # Добавляем jti (JWT ID) и микросекунды для уникальности
            payload = {
                'sub': str(user_id),
                'exp': expire,
                'iat': now,
                'jti': str(uuid.uuid4()),  # Уникальный ID токена
                'nbf': now,  # Not before
                'type': 'refresh'
            }
            
            token = jwt.encode(
                payload,
                config.JWT_SECRET_KEY,
                algorithm=config.JWT_ALGORITHM
            )
            
            return token
            
        except Exception as e:
            logger.error(f"Error creating refresh token: {e}")
            raise
    
    def validate_access_token(self, token: str) -> Dict[str, Any]:
        """
        Валидировать access token
        
        Args:
            token: JWT токен
            
        Returns:
            Словарь с результатами валидации
        """
        try:
            payload = jwt.decode(
                token,
                config.JWT_SECRET_KEY,
                algorithms=[config.JWT_ALGORITHM]
            )
            
            # Проверить тип токена
            if payload.get('type') != 'access':
                return {'valid': False, 'error': 'Invalid token type'}
            
            return {'valid': True, 'payload': payload}
            
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token expired'}
        except jwt.InvalidTokenError as e:
            return {'valid': False, 'error': f'Invalid token: {str(e)}'}
        except Exception as e:
            logger.error(f"Error validating access token: {e}")
            return {'valid': False, 'error': 'Token validation error'}
    
    def validate_refresh_token(self, token: str) -> Dict[str, Any]:
        """
        Валидировать refresh token
        
        Args:
            token: JWT токен
            
        Returns:
            Словарь с результатами валидации
        """
        try:
            payload = jwt.decode(
                token,
                config.JWT_SECRET_KEY,
                algorithms=[config.JWT_ALGORITHM]
            )
            
            # Проверить тип токена
            if payload.get('type') != 'refresh':
                return {'valid': False, 'error': 'Invalid token type'}
            
            return {'valid': True, 'payload': payload}
            
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token expired'}
        except jwt.InvalidTokenError as e:
            return {'valid': False, 'error': f'Invalid token: {str(e)}'}
        except Exception as e:
            logger.error(f"Error validating refresh token: {e}")
            return {'valid': False, 'error': 'Token validation error'}
    
    def decode_token_without_verification(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Декодировать токен без проверки (для отладки)
        
        Args:
            token: JWT токен
            
        Returns:
            Payload токена или None
        """
        try:
            return jwt.decode(
                token,
                options={"verify_signature": False}
            )
        except Exception:
            return None


# Singleton instance
token_service = TokenService()

