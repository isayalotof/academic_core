"""
Configuration for ms-schedule
Конфигурация из переменных окружения
"""

import os
from typing import Optional


class Config:
    """Schedule service configuration"""
    
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
    
    # ============ RPC CLIENTS ============
    MS_AUDIT_HOST: str = os.getenv('MS_AUDIT_HOST', 'localhost')
    MS_AUDIT_PORT: int = int(os.getenv('MS_AUDIT_PORT', 50051))
    MS_AGENT_HOST: str = os.getenv('MS_AGENT_HOST', 'localhost')
    MS_AGENT_PORT: int = int(os.getenv('MS_AGENT_PORT', 50053))
    
    # ============ gRPC SERVER ============
    GRPC_PORT: int = int(os.getenv('GRPC_PORT', 50055))
    GRPC_MAX_WORKERS: int = int(os.getenv('GRPC_MAX_WORKERS', 10))
    GRPC_MAX_MESSAGE_LENGTH: int = 100 * 1024 * 1024  # 100MB
    
    # ============ TIMEZONE ============
    TIMEZONE: str = os.getenv('TIMEZONE', 'Asia/Vladivostok')
    
    # ============ EXPORT SETTINGS ============
    EXPORT_DIR: str = os.getenv('EXPORT_DIR', '/app/exports')
    MAX_EXPORT_SIZE_MB: int = int(os.getenv('MAX_EXPORT_SIZE_MB', 50))
    
    # ============ TIME SLOTS ============
    TIME_SLOTS = {
        1: ("09:00", "10:30"),
        2: ("10:45", "12:15"),
        3: ("13:00", "14:30"),
        4: ("14:45", "16:15"),
        5: ("16:30", "18:00"),
        6: ("18:15", "19:45")
    }
    
    # ============ LOGGING ============
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # ============ SERVICE INFO ============
    SERVICE_NAME: str = 'ms-schedule'
    SERVICE_VERSION: str = '1.0.0'
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')
    
    @classmethod
    def validate(cls) -> bool:
        """Validate critical configuration"""
        if cls.ENVIRONMENT == 'production':
            if not cls.DB_PASSWORD or cls.DB_PASSWORD == 'university_pass':
                return False
        return True
    
    @classmethod
    def get_db_url(cls) -> str:
        """Get database connection URL"""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"


# Singleton instance
config = Config()

