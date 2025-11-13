"""
Redis Cache Manager
Управление кэшированием через Redis
"""

import redis
import os
import pickle
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


class Cache:
    """Redis кэш менеджер"""
    
    def __init__(self):
        """Инициализация Redis подключения"""
        try:
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                password=os.getenv('REDIS_PASSWORD'),
                db=0,
                decode_responses=False,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Caching disabled.")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return pickle.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Сохранить значение в кэш"""
        if not self.redis_client:
            return False
        
        try:
            serialized = pickle.dumps(value)
            self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Удалить значение из кэша"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Инвалидировать все ключи по паттерну"""
        if not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache invalidate pattern error for {pattern}: {e}")
            return 0


# Singleton instance
cache = Cache()

