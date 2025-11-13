"""
Configuration Management
Управление конфигурацией из переменных окружения
"""

import os
from typing import Optional


class Config:
    """Application configuration from environment variables"""
    
    # ============ DATABASE ============
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', 5432))
    DB_NAME: str = os.getenv('DB_NAME', 'university_db')
    DB_USER: str = os.getenv('DB_USER', 'university_user')
    DB_PASSWORD: Optional[str] = os.getenv('DB_PASSWORD')
    DB_POOL_MIN: int = int(os.getenv('DB_POOL_MIN', 5))
    DB_POOL_MAX: int = int(os.getenv('DB_POOL_MAX', 20))
    
    # ============ REDIS ============
    REDIS_HOST: str = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD: Optional[str] = os.getenv('REDIS_PASSWORD')
    REDIS_DB: int = int(os.getenv('REDIS_DB', 0))
    
    # ============ JWT ============
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', 'change_me_in_production')
    JWT_ALGORITHM: str = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', 15))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS', 30))
    
    # ============ SECURITY ============
    BCRYPT_ROUNDS: int = int(os.getenv('BCRYPT_ROUNDS', 12))
    MAX_LOGIN_ATTEMPTS: int = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))
    LOCKOUT_DURATION_MINUTES: int = int(os.getenv('LOCKOUT_DURATION_MINUTES', 30))
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = int(os.getenv('PASSWORD_RESET_TOKEN_EXPIRE_HOURS', 24))
    
    # ============ GRPC ============
    GRPC_PORT: int = int(os.getenv('GRPC_PORT', 50052))
    GRPC_MAX_WORKERS: int = int(os.getenv('GRPC_MAX_WORKERS', 10))
    GRPC_MAX_MESSAGE_LENGTH: int = int(os.getenv('GRPC_MAX_MESSAGE_LENGTH', 4 * 1024 * 1024))
    
    # ============ APPLICATION ============
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    SERVICE_NAME: str = 'ms-auth'
    SERVICE_VERSION: str = '1.0.0'
    
    # ============ CACHE ============
    CACHE_TTL: int = int(os.getenv('CACHE_TTL', 300))
    CACHE_ENABLED: bool = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required = [
            cls.DB_PASSWORD,
            cls.JWT_SECRET_KEY
        ]
        
        if cls.ENVIRONMENT == 'production':
            for value in required:
                if not value or value == 'change_me_in_production':
                    return False
        
        return True
    
    @classmethod
    def to_dict(cls) -> dict:
        """Convert configuration to dictionary (excluding passwords)"""
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and 'PASSWORD' not in key and 'SECRET' not in key
        }


config = Config()

