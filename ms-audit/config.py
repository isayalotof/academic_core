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
    
    # ============ RABBITMQ ============
    RABBITMQ_HOST: str = os.getenv('RABBITMQ_HOST', 'localhost')
    RABBITMQ_PORT: int = int(os.getenv('RABBITMQ_PORT', 5672))
    RABBITMQ_USER: str = os.getenv('RABBITMQ_USER', 'university_user')
    RABBITMQ_PASSWORD: Optional[str] = os.getenv('RABBITMQ_PASSWORD')
    
    # ============ GRPC ============
    GRPC_PORT: int = int(os.getenv('GRPC_PORT', 50051))
    GRPC_MAX_WORKERS: int = int(os.getenv('GRPC_MAX_WORKERS', 10))
    GRPC_MAX_MESSAGE_LENGTH: int = int(os.getenv('GRPC_MAX_MESSAGE_LENGTH', 4 * 1024 * 1024))  # 4MB
    
    # ============ APPLICATION ============
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    SERVICE_NAME: str = 'ms-audit'
    SERVICE_VERSION: str = '1.0.0'
    
    # ============ METRICS ============
    METRICS_PORT: int = int(os.getenv('METRICS_PORT', 8001))
    ENABLE_METRICS: bool = os.getenv('ENABLE_METRICS', 'true').lower() == 'true'
    
    # ============ CACHE ============
    CACHE_TTL: int = int(os.getenv('CACHE_TTL', 300))  # 5 minutes
    CACHE_ENABLED: bool = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required = [
            cls.DB_PASSWORD,
            cls.REDIS_PASSWORD,
            cls.RABBITMQ_PASSWORD
        ]
        
        if cls.ENVIRONMENT == 'production':
            for value in required:
                if not value:
                    return False
        
        return True
    
    @classmethod
    def to_dict(cls) -> dict:
        """Convert configuration to dictionary (excluding passwords)"""
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and 'PASSWORD' not in key
        }


config = Config()

