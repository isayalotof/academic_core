"""
Configuration for ms-agent
Конфигурация из переменных окружения
"""

import os
from typing import Optional


class Config:
    """Agent service configuration"""
    
    # ============ DATABASE ============
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', 5432))
    DB_NAME: str = os.getenv('DB_NAME', 'university_db')
    DB_USER: str = os.getenv('DB_USER', 'university_user')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', 'university_pass')
    DB_POOL_MIN: int = int(os.getenv('DB_POOL_MIN', 2))
    DB_POOL_MAX: int = int(os.getenv('DB_POOL_MAX', 10))
    
    # ============ REDIS ============
    REDIS_HOST: str = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD: Optional[str] = os.getenv('REDIS_PASSWORD')
    CACHE_ENABLED: bool = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    CACHE_TTL: int = int(os.getenv('CACHE_TTL', 3600))  # 1 час
    
    # ============ GIGACHAT API ============
    GIGACHAT_CLIENT_ID: str = os.getenv('GIGACHAT_CLIENT_ID', '')
    GIGACHAT_CLIENT_SECRET: str = os.getenv('GIGACHAT_CLIENT_SECRET', '')
    GIGACHAT_SCOPE: str = os.getenv('GIGACHAT_SCOPE', 'GIGACHAT_API_PERS')
    GIGACHAT_MODEL: str = os.getenv('GIGACHAT_MODEL', 'GigaChat')
    GIGACHAT_TEMPERATURE: float = float(os.getenv('GIGACHAT_TEMPERATURE', 0.7))
    GIGACHAT_MAX_TOKENS: int = int(os.getenv('GIGACHAT_MAX_TOKENS', 2000))
    
    # ============ RPC CLIENTS ============
    MS_AUDIT_HOST: str = os.getenv('MS_AUDIT_HOST', 'localhost')
    MS_AUDIT_PORT: int = int(os.getenv('MS_AUDIT_PORT', 50051))
    
    # ⭐ ms-core - для получения предпочтений преподавателей (KEY!)
    MS_CORE_HOST: str = os.getenv('MS_CORE_HOST', 'localhost')
    MS_CORE_PORT: int = int(os.getenv('MS_CORE_PORT', 50054))
    
    # ⭐ ms-schedule - для создания занятий (BulkCreateLessons)
    MS_SCHEDULE_HOST: str = os.getenv('MS_SCHEDULE_HOST', 'localhost')
    MS_SCHEDULE_PORT: int = int(os.getenv('MS_SCHEDULE_PORT', 50055))
    
    # ============ gRPC SERVER ============
    GRPC_PORT: int = int(os.getenv('GRPC_PORT', 50053))
    GRPC_MAX_WORKERS: int = int(os.getenv('GRPC_MAX_WORKERS', 10))
    GRPC_MAX_MESSAGE_LENGTH: int = 100 * 1024 * 1024  # 100MB
    
    # ============ AGENT SETTINGS ============
    MAX_ITERATIONS: int = int(os.getenv('MAX_ITERATIONS', 100))
    STAGE1_MAX_ITERATIONS: int = int(os.getenv('STAGE1_MAX_ITERATIONS', 80))
    STAGE2_MAX_ITERATIONS: int = int(os.getenv('STAGE2_MAX_ITERATIONS', 50))
    
    # Критерий остановки (если скор не улучшился за N итераций)
    EARLY_STOPPING_PATIENCE: int = int(os.getenv('EARLY_STOPPING_PATIENCE', 15))
    
    # Критерий успеха (процент улучшения)
    MIN_IMPROVEMENT_THRESHOLD: float = float(os.getenv('MIN_IMPROVEMENT_THRESHOLD', 0.01))  # 1%
    
    # ============ LOGGING ============
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # ============ SERVICE INFO ============
    SERVICE_NAME: str = 'ms-agent'
    SERVICE_VERSION: str = '1.0.0'
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')
    
    @classmethod
    def validate(cls) -> bool:
        """Validate critical configuration"""
        if cls.ENVIRONMENT == 'production':
            if not cls.GIGACHAT_CLIENT_ID or not cls.GIGACHAT_CLIENT_SECRET:
                return False
            if not cls.DB_PASSWORD or cls.DB_PASSWORD == 'university_pass':
                return False
        return True
    
    @classmethod
    def get_db_url(cls) -> str:
        """Get database connection URL"""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"


# Singleton instance
config = Config()

