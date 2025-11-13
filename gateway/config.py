"""
Gateway Configuration
Конфигурация API Gateway из переменных окружения
"""

import os
from typing import List


class Config:
    """Gateway configuration from environment variables"""
    
    # ============ MICROSERVICES ============
    MS_AUTH_HOST: str = os.getenv('MS_AUTH_HOST', 'localhost')
    MS_AUTH_PORT: int = int(os.getenv('MS_AUTH_PORT', 50052))
    MS_AUDIT_HOST: str = os.getenv('MS_AUDIT_HOST', 'localhost')
    MS_AUDIT_PORT: int = int(os.getenv('MS_AUDIT_PORT', 50051))
    MS_AGENT_HOST: str = os.getenv('MS_AGENT_HOST', 'localhost')
    MS_AGENT_PORT: int = int(os.getenv('MS_AGENT_PORT', 50053))
    MS_CORE_HOST: str = os.getenv('MS_CORE_HOST', 'localhost')
    MS_CORE_PORT: int = int(os.getenv('MS_CORE_PORT', 50054))
    MS_SCHEDULE_HOST: str = os.getenv('MS_SCHEDULE_HOST', 'localhost')
    MS_SCHEDULE_PORT: int = int(os.getenv('MS_SCHEDULE_PORT', 50055))
    
    # ============ DATABASE ============
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', 5432))
    DB_NAME: str = os.getenv('DB_NAME', 'university_db')
    DB_USER: str = os.getenv('DB_USER', 'university_user')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', '')
    
    # ============ REDIS ============
    REDIS_HOST: str = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD: str = os.getenv('REDIS_PASSWORD', '')
    
    # ============ JWT ============
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', 'change_me_in_production')
    JWT_ALGORITHM: str = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRE_MINUTES: int = int(os.getenv('JWT_EXPIRE_MINUTES', 1440))
    
    # ============ CORS ============
    CORS_ORIGINS: List[str] = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # ============ APPLICATION ============
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    SERVICE_NAME: str = 'gateway'
    SERVICE_VERSION: str = '1.0.0'
    
    # ============ API ============
    API_PREFIX: str = '/api'
    DOCS_URL: str = '/docs'
    REDOC_URL: str = '/redoc'
    OPENAPI_URL: str = '/openapi.json'
    
    @classmethod
    def to_dict(cls) -> dict:
        """Convert configuration to dictionary (excluding passwords)"""
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and 'PASSWORD' not in key and 'SECRET' not in key
        }


config = Config()

