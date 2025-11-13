"""
Redis caching client for ms-core
"""
import redis
import json
import logging
from typing import Any, Optional
import os

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis кэш для ms-core"""
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        password: str = None,
        db: int = 0,
        default_ttl: int = 3600
    ):
        """
        Инициализация Redis клиента
        
        Args:
            host: Redis host (или из env)
            port: Redis port (или из env)
            password: Redis password (или из env)
            db: Redis database number
            default_ttl: TTL по умолчанию (секунды)
        """
        self.host = host or os.getenv('REDIS_HOST', 'localhost')
        self.port = port or int(os.getenv('REDIS_PORT', 6379))
        self.password = password or os.getenv('REDIS_PASSWORD')
        self.db = db
        self.default_ttl = default_ttl
        
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                decode_responses=True
            )
            # Test connection
            self.client.ping()
            logger.info(f"✓ Connected to Redis: {self.host}:{self.port}")
        except Exception as e:
            logger.warning(f"✗ Failed to connect to Redis: {e}")
            self.client = None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        Сохранить значение в кэш
        
        Args:
            key: Ключ
            value: Значение (будет сериализовано в JSON)
            ttl: TTL в секундах (None = использовать default)
        
        Returns:
            True если успешно
        """
        if not self.client:
            return False
        
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value, ensure_ascii=False)
            self.client.setex(key, ttl, serialized)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache SET error: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Получить значение из кэша
        
        Args:
            key: Ключ
        
        Returns:
            Значение или None
        """
        if not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value is None:
                logger.debug(f"Cache MISS: {key}")
                return None
            
            logger.debug(f"Cache HIT: {key}")
            return json.loads(value)
        except Exception as e:
            logger.error(f"Cache GET error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        Удалить значение из кэша
        
        Args:
            key: Ключ
        
        Returns:
            True если успешно
        """
        if not self.client:
            return False
        
        try:
            self.client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache DELETE error: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Удалить ключи по паттерну
        
        Args:
            pattern: Паттерн (например: "teacher:*")
        
        Returns:
            Количество удалённых ключей
        """
        if not self.client:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                count = self.client.delete(*keys)
                logger.debug(f"Cache DELETE pattern: {pattern} ({count} keys)")
                return count
            return 0
        except Exception as e:
            logger.error(f"Cache DELETE pattern error: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """
        Проверить существование ключа
        
        Args:
            key: Ключ
        
        Returns:
            True если ключ существует
        """
        if not self.client:
            return False
        
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache EXISTS error: {e}")
            return False


# Глобальный экземпляр кэша
_cache: Optional[RedisCache] = None


def get_cache() -> RedisCache:
    """Получить глобальный экземпляр кэша"""
    global _cache
    if _cache is None:
        _cache = RedisCache()
    return _cache

