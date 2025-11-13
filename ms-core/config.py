"""
Configuration for ms-core
Load from environment variables
"""
import os


class Config:
    """Configuration class"""
    
    # Service info
    SERVICE_NAME: str = 'ms-core'
    SERVICE_VERSION: str = '1.0.0'
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')
    
    # Database
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', 5432))
    DB_NAME: str = os.getenv('DB_NAME', 'university_db')
    DB_USER: str = os.getenv('DB_USER', 'university_user')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', 'university_pass')
    DB_POOL_MIN: int = int(os.getenv('DB_POOL_MIN', 2))
    DB_POOL_MAX: int = int(os.getenv('DB_POOL_MAX', 10))
    
    # Redis
    REDIS_HOST: str = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD: str = os.getenv('REDIS_PASSWORD', '')
    REDIS_DB: int = int(os.getenv('REDIS_DB', 0))
    
    # Cache settings
    CACHE_ENABLED: bool = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    CACHE_TTL: int = int(os.getenv('CACHE_TTL', 3600))  # 1 hour
    CACHE_TTL_TEACHERS: int = int(os.getenv('CACHE_TTL_TEACHERS', 1800))  # 30 min
    CACHE_TTL_PREFERENCES: int = int(os.getenv('CACHE_TTL_PREFERENCES', 900))  # 15 min
    
    # gRPC
    GRPC_PORT: int = int(os.getenv('GRPC_PORT', 50054))
    GRPC_MAX_WORKERS: int = int(os.getenv('GRPC_MAX_WORKERS', 10))
    
    # RPC клиенты (для интеграции)
    MS_AUTH_HOST: str = os.getenv('MS_AUTH_HOST', 'localhost')
    MS_AUTH_PORT: int = int(os.getenv('MS_AUTH_PORT', 50052))
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_JSON: bool = os.getenv('LOG_JSON', 'true').lower() == 'true'
    
    # Excel import
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv('MAX_UPLOAD_SIZE_MB', 10))
    UPLOAD_DIR: str = os.getenv('UPLOAD_DIR', '/app/uploads')
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = int(os.getenv('DEFAULT_PAGE_SIZE', 50))
    MAX_PAGE_SIZE: int = int(os.getenv('MAX_PAGE_SIZE', 200))
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        required = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        missing = [key for key in required if not getattr(cls, key)]
        
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")
    
    @classmethod
    def to_dict(cls) -> dict:
        """Convert config to dictionary"""
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and key.isupper()
        }


# Create config instance
config = Config()

