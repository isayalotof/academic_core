"""
Configuration for ms-events
"""
import os

class Config:
    SERVICE_NAME: str = 'ms-events'
    SERVICE_VERSION: str = '1.0.0'
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', 5432))
    DB_NAME: str = os.getenv('DB_NAME', 'university_db')
    DB_USER: str = os.getenv('DB_USER', 'university_user')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', 'university_pass')
    DB_POOL_MIN: int = int(os.getenv('DB_POOL_MIN', 2))
    DB_POOL_MAX: int = int(os.getenv('DB_POOL_MAX', 10))
    REDIS_HOST: str = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD: str = os.getenv('REDIS_PASSWORD', '')
    REDIS_DB: int = int(os.getenv('REDIS_DB', 0))
    CACHE_ENABLED: bool = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    CACHE_TTL: int = int(os.getenv('CACHE_TTL', 3600))
    GRPC_PORT: int = int(os.getenv('GRPC_PORT', 50057))
    GRPC_MAX_WORKERS: int = int(os.getenv('GRPC_MAX_WORKERS', 10))
    MS_CORE_HOST: str = os.getenv('MS_CORE_HOST', 'localhost')
    MS_CORE_PORT: int = int(os.getenv('MS_CORE_PORT', 50054))
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_JSON: bool = os.getenv('LOG_JSON', 'true').lower() == 'true'
    DEFAULT_PAGE_SIZE: int = int(os.getenv('DEFAULT_PAGE_SIZE', 50))
    MAX_PAGE_SIZE: int = int(os.getenv('MAX_PAGE_SIZE', 200))
    
    @classmethod
    def validate(cls):
        required = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")

config = Config()

