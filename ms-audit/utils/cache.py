"""
Redis Cache Manager
Управление кэшированием через Redis
"""

import redis
import os
import json
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
        """
        Получить значение из кэша
        
        Args:
            key: Ключ кэша
            
        Returns:
            Закэшированное значение или None
        """
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
    
    def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = 300
    ) -> bool:
        """
        Сохранить значение в кэш
        
        Args:
            key: Ключ кэша
            value: Значение для сохранения
            ttl: Время жизни в секундах (по умолчанию 5 минут)
            
        Returns:
            True если успешно, False иначе
        """
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
        """
        Удалить значение из кэша
        
        Args:
            key: Ключ кэша
            
        Returns:
            True если успешно, False иначе
        """
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Инвалидировать все ключи по паттерну
        
        Args:
            pattern: Паттерн ключей (например, 'classrooms:*')
            
        Returns:
            Количество удаленных ключей
        """
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
    
    def exists(self, key: str) -> bool:
        """
        Проверить существование ключа
        
        Args:
            key: Ключ кэша
            
        Returns:
            True если ключ существует
        """
        if not self.redis_client:
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Инкрементировать счетчик
        
        Args:
            key: Ключ счетчика
            amount: Величина инкремента
            
        Returns:
            Новое значение или None
        """
        if not self.redis_client:
            return None
        
        try:
            return self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None
    
    def close(self) -> None:
        """Закрыть соединение с Redis"""
        if self.redis_client:
            self.redis_client.close()
            logger.info("Redis connection closed")


# Singleton instance
cache = Cache()

