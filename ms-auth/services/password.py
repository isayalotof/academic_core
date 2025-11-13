"""
Password Service
Сервис для хеширования и проверки паролей
"""

import bcrypt
import logging
from config import config

logger = logging.getLogger(__name__)


class PasswordService:
    """Сервис для работы с паролями"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Хешировать пароль с использованием bcrypt
        
        Args:
            password: Пароль в открытом виде
            
        Returns:
            Хеш пароля
        """
        try:
            salt = bcrypt.gensalt(rounds=config.BCRYPT_ROUNDS)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Проверить пароль
        
        Args:
            password: Пароль в открытом виде
            password_hash: Хеш пароля
            
        Returns:
            True если пароль правильный
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False


# Singleton instance
password_service = PasswordService()

