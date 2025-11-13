"""
Redis caching client for ms-schedule
Кэширование расписания для быстрого доступа
"""

import redis
import json
from typing import Optional, Any
import logging

from config import config

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis caching client"""
    
    def __init__(self):
        """Initialize Redis connection"""
        self._client: Optional[redis.Redis] = None
        if config.CACHE_ENABLED:
            self._connect()
    
    def _connect(self) -> None:
        """Connect to Redis"""
        try:
            self._client = redis.Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                password=config.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            self._client.ping()
            logger.info(f"✅ Redis connected: {config.REDIS_HOST}:{config.REDIS_PORT}")
            
        except redis.RedisError as e:
            logger.warning(f"⚠️  Redis connection failed: {e}. Caching disabled.")
            self._client = None
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if not self._client:
            return None
        
        try:
            value = self._client.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            else:
                logger.debug(f"Cache MISS: {key}")
                return None
                
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default from config)
            
        Returns:
            True if successful
        """
        if not self._client:
            return False
        
        try:
            ttl = ttl or config.CACHE_TTL
            serialized = json.dumps(value, ensure_ascii=False)
            self._client.setex(key, ttl, serialized)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, *keys: str) -> bool:
        """
        Delete keys from cache
        
        Args:
            keys: Cache keys to delete
            
        Returns:
            True if successful
        """
        if not self._client or not keys:
            return False
        
        try:
            self._client.delete(*keys)
            logger.debug(f"Cache DELETE: {', '.join(keys)}")
            return True
            
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching pattern
        
        Args:
            pattern: Key pattern (e.g., "schedule:group:*")
            
        Returns:
            Number of deleted keys
        """
        if not self._client:
            return 0
        
        try:
            keys = list(self._client.scan_iter(match=pattern))
            if keys:
                count = self._client.delete(*keys)
                logger.info(f"Cache invalidated: {count} keys matching '{pattern}'")
                return count
            return 0
            
        except Exception as e:
            logger.error(f"Cache invalidate error: {e}")
            return 0
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self._client:
            return {'enabled': False}
        
        try:
            info = self._client.info('stats')
            return {
                'enabled': True,
                'hits': info.get('keyspace_hits', 0),
                'misses': info.get('keyspace_misses', 0),
                'keys': self._client.dbsize()
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {'enabled': True, 'error': str(e)}
    
    def close(self) -> None:
        """Close Redis connection"""
        if self._client:
            try:
                self._client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Redis close error: {e}")


# Global cache instance
cache = RedisCache()


# Helper functions for schedule caching
def get_cache_key(entity_type: str, entity_id: int, semester: int, academic_year: str, **kwargs) -> str:
    """
    Generate cache key for schedule
    
    Args:
        entity_type: 'group', 'teacher', 'classroom'
        entity_id: ID of entity
        semester: Semester number
        academic_year: Academic year
        **kwargs: Additional parameters
    """
    base = f"schedule:{entity_type}:{entity_id}:{semester}:{academic_year}"
    
    if kwargs:
        params = ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()) if v is not None)
        return f"{base}:{params}" if params else base
    
    return base


def invalidate_schedule_cache(semester: int, academic_year: str) -> None:
    """Invalidate all schedule cache for semester"""
    pattern = f"schedule:*:{semester}:{academic_year}*"
    cache.invalidate_pattern(pattern)

