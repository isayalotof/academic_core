"""
Authentication Service
Сервис для аутентификации и регистрации пользователей
"""

import hashlib
import uuid
import logging
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timedelta

from db.connection import db
from db.queries import users as user_queries
from db.queries import tokens as token_queries
from db.queries import login_history as history_queries
from services.password import password_service
from services.token import token_service
from services.user_crud import user_crud
from config import config

logger = logging.getLogger(__name__)


class AuthService:
    """Сервис аутентификации"""
    
    def register(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str,
        phone: Optional[str],
        primary_role: str,
        teacher_id: Optional[int] = None,
        student_group_id: Optional[int] = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Регистрация нового пользователя
        
        Returns:
            Tuple (user, tokens)
        """
        try:
            # Проверить существование
            exists = user_crud.check_exists(username, email)
            if exists['username_exists']:
                raise ValueError("Username already exists")
            if exists['email_exists']:
                raise ValueError("Email already exists")
            
            # Хешировать пароль
            password_hash = password_service.hash_password(password)
            
            # Создать пользователя
            user_data = {
                'username': username,
                'email': email,
                'password_hash': password_hash,
                'full_name': full_name,
                'phone': phone,
                'primary_role': primary_role,
                'teacher_id': teacher_id,
                'student_group_id': student_group_id
            }
            
            user = user_crud.create(user_data)
            
            # Создать токены
            tokens = self._create_token_pair(user, '', '', '')
            
            logger.info(f"User registered: {username} (ID: {user['id']})")
            
            return user, tokens
            
        except ValueError as e:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Error in register: {e}", exc_info=True)
            raise
    
    def login(
        self,
        username: str,
        password: str,
        ip_address: str = '',
        user_agent: str = '',
        device_id: str = ''
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Вход пользователя
        
        Returns:
            Tuple (user, tokens)
        """
        try:
            # Получить пользователя (по username или email)
            user = user_crud.get_by_username(username)
            if not user:
                user = user_crud.get_by_email(username)
            
            if not user:
                self._log_login_attempt(None, username, False, ip_address, user_agent, 'user_not_found')
                raise ValueError("Invalid credentials")
            
            # Проверить активность
            if not user['is_active']:
                self._log_login_attempt(user['id'], username, False, ip_address, user_agent, 'account_inactive')
                raise ValueError("Account is inactive")
            
            # Проверить блокировку
            if self._is_user_locked(user['id']):
                locked_until = user.get('locked_until')
                self._log_login_attempt(user['id'], username, False, ip_address, user_agent, 'account_locked')
                raise ValueError(f"Account is locked until {locked_until}")
            
            # Проверить пароль
            if not password_service.verify_password(password, user['password_hash']):
                self._increment_failed_attempts(user['id'])
                self._log_login_attempt(user['id'], username, False, ip_address, user_agent, 'invalid_password')
                raise ValueError("Invalid credentials")
            
            # Успешный вход
            self._reset_failed_attempts(user['id'], ip_address)
            self._log_login_attempt(user['id'], username, True, ip_address, user_agent, None)
            
            # Создать токены
            tokens = self._create_token_pair(user, ip_address, user_agent, device_id)
            
            logger.info(f"User logged in: {username} (IP: {ip_address})")
            
            return user, tokens
            
        except ValueError as e:
            # Re-raise authentication errors
            raise
        except Exception as e:
            logger.error(f"Error in login: {e}", exc_info=True)
            raise
    
    def logout(self, user_id: int, refresh_token: str) -> bool:
        """Выход пользователя (отозвать refresh token)"""
        try:
            # Отозвать токен
            token_hash = self._hash_token(refresh_token)
            db.execute_query(
                token_queries.REVOKE_REFRESH_TOKEN,
                {'token': token_hash},
                fetch=False
            )
            
            logger.info(f"User logged out: ID={user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error in logout: {e}")
            return False
    
    def refresh_tokens(
        self,
        refresh_token: str,
        ip_address: str = '',
        user_agent: str = ''
    ) -> Dict[str, Any]:
        """Обновить токены с rotation"""
        try:
            # Валидация токена
            validation = token_service.validate_refresh_token(refresh_token)
            if not validation['valid']:
                raise ValueError(validation['error'])
            
            # Получить токен из БД
            token_hash = self._hash_token(refresh_token)
            result = db.execute_query(
                token_queries.SELECT_REFRESH_TOKEN,
                {'token': token_hash},
                fetch=True
            )
            
            if not result or len(result) == 0:
                raise ValueError("Invalid refresh token")
            
            old_token = dict(result[0])
            
            # Проверить использование (защита от rotation attack)
            if old_token['used_at']:
                logger.warning(f"Token reuse detected! Revoking family: {old_token['token_family']}")
                db.execute_query(
                    token_queries.REVOKE_TOKEN_FAMILY,
                    {'token_family': old_token['token_family']},
                    fetch=False
                )
                raise ValueError("Token reuse detected. All tokens revoked.")
            
            # Пометить как использованный
            db.execute_query(
                token_queries.MARK_TOKEN_USED,
                {'token_id': old_token['id']},
                fetch=False
            )
            
            # Получить пользователя
            user = user_crud.get_by_id(old_token['user_id'])
            if not user or not user['is_active']:
                raise ValueError("User not found or inactive")
            
            # Создать новую пару токенов (та же семья)
            new_tokens = self._create_token_pair(
                user,
                ip_address,
                user_agent,
                old_token.get('device_id', ''),
                token_family=old_token['token_family']
            )
            
            logger.info(f"Tokens refreshed for user: {user['id']}")
            
            return new_tokens
            
        except ValueError as e:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Error refreshing tokens: {e}", exc_info=True)
            raise
    
    # ========== Helper Methods ==========
    
    def _create_token_pair(
        self,
        user: Dict[str, Any],
        ip_address: str,
        user_agent: str,
        device_id: str,
        token_family: Optional[str] = None
    ) -> Dict[str, Any]:
        """Создать пару токенов (access + refresh)"""
        import psycopg2
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # Access token
                access_token = token_service.create_access_token(
                    user['id'],
                    user['username'],
                    user['primary_role'],
                    user.get('roles', [])
                )
                
                # Refresh token - генерируем заново при каждой попытке
                refresh_token = token_service.create_refresh_token(user['id'])
                
                # Сохранить refresh token в БД
                if not token_family:
                    token_family = str(uuid.uuid4())
                
                token_hash = self._hash_token(refresh_token)
                expires_at = datetime.utcnow() + timedelta(
                    days=config.JWT_REFRESH_TOKEN_EXPIRE_DAYS
                )
                
                db.execute_query(
                    token_queries.INSERT_REFRESH_TOKEN,
                    {
                        'user_id': user['id'],
                        'token': token_hash,
                        'token_family': token_family,
                        'expires_at': expires_at,
                        'ip_address': ip_address,
                        'user_agent': user_agent,
                        'device_id': device_id
                    },
                    fetch=False
                )
                
                return {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'expires_in': config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                    'token_type': 'Bearer'
                }
                
            except psycopg2.errors.UniqueViolation as e:
                # Коллизия токена - пробуем снова
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Token hash collision detected (attempt {attempt + 1}/{max_retries}), "
                        f"retrying with new token..."
                    )
                    continue
                else:
                    logger.error(f"Token hash collision after {max_retries} attempts: {e}")
                    raise Exception("Failed to generate unique token after multiple attempts")
            except Exception as e:
                logger.error(f"Error creating token pair: {e}")
                raise
    
    @staticmethod
    def _hash_token(token: str) -> str:
        """Хешировать токен для хранения в БД"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def _is_user_locked(self, user_id: int) -> bool:
        """Проверить заблокирован ли пользователь"""
        try:
            result = db.execute_query(
                user_queries.CHECK_USER_LOCKED,
                {'user_id': user_id, 'max_attempts': config.MAX_LOGIN_ATTEMPTS},
                fetch=True
            )
            
            if result and len(result) > 0:
                return result[0]['is_currently_locked']
            return False
            
        except Exception as e:
            logger.error(f"Error checking user lock: {e}")
            return False
    
    def _increment_failed_attempts(self, user_id: int) -> None:
        """Увеличить счетчик неудачных попыток"""
        try:
            db.execute_query(
                user_queries.INCREMENT_FAILED_ATTEMPTS,
                {
                    'user_id': user_id,
                    'max_attempts': config.MAX_LOGIN_ATTEMPTS,
                    'lockout_minutes': config.LOCKOUT_DURATION_MINUTES
                },
                fetch=False
            )
        except Exception as e:
            logger.error(f"Error incrementing failed attempts: {e}")
    
    def _reset_failed_attempts(self, user_id: int, ip_address: str) -> None:
        """Сбросить счетчик неудачных попыток"""
        try:
            db.execute_query(
                user_queries.RESET_FAILED_ATTEMPTS,
                {'user_id': user_id, 'ip_address': ip_address},
                fetch=False
            )
        except Exception as e:
            logger.error(f"Error resetting failed attempts: {e}")
    
    def _log_login_attempt(
        self,
        user_id: Optional[int],
        username: str,
        success: bool,
        ip_address: str,
        user_agent: str,
        failure_reason: Optional[str]
    ) -> None:
        """Залогировать попытку входа"""
        try:
            db.execute_query(
                history_queries.INSERT_LOGIN_HISTORY,
                {
                    'user_id': user_id,
                    'username': username,
                    'success': success,
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'failure_reason': failure_reason
                },
                fetch=False
            )
        except Exception as e:
            logger.error(f"Error logging login attempt: {e}")


# Singleton instance
auth_service = AuthService()

