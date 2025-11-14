"""
Database Connection Pool
Управление пулом соединений для PostgreSQL
"""

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any
import logging
from contextlib import contextmanager

from config import config

logger = logging.getLogger(__name__)


class DatabasePool:
    """PostgreSQL connection pool manager"""
    
    def __init__(self):
        """Initialize connection pool"""
        self.pool: Optional[pool.ThreadedConnectionPool] = None
        self._create_pool()
    
    def _create_pool(self):
        """Create connection pool"""
        try:
            self.pool = pool.ThreadedConnectionPool(
                minconn=config.DB_POOL_MIN,
                maxconn=config.DB_POOL_MAX,
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                cursor_factory=RealDictCursor
            )
            logger.info(
                f"✓ Database pool created: {config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME} "
                f"(min={config.DB_POOL_MIN}, max={config.DB_POOL_MAX})"
            )
        except Exception as e:
            logger.error(f"✗ Failed to create database pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Get connection from pool
        
        Usage:
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
        """
        if self.pool is None:
            raise RuntimeError("Database pool not initialized")
        
        conn = None
        try:
            conn = self.pool.getconn()
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                self.pool.putconn(conn)
    
    def execute_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        fetch: bool = True
    ) -> Optional[List[Dict]]:
        """
        Execute SQL query
        
        Args:
            query: SQL query with %(param)s placeholders
            params: Query parameters
            fetch: Whether to fetch results
        
        Returns:
            List of dicts if fetch=True, None otherwise
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params or {})
                
                if fetch:
                    results = cur.fetchall()
                    conn.commit()  # Коммитим транзакцию даже при fetch=True
                    return [dict(row) for row in results] if results else []
                else:
                    conn.commit()
                    return None
    
    def execute_many(
        self,
        query: str,
        params_list: List[Dict[str, Any]]
    ) -> int:
        """
        Execute query multiple times with different parameters
        
        Args:
            query: SQL query
            params_list: List of parameter dicts
        
        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Convert list of dicts to list of tuples
                for params in params_list:
                    cur.execute(query, params)
                
                conn.commit()
                return cur.rowcount
    
    def execute_transaction(
        self,
        queries: List[tuple]
    ) -> bool:
        """
        Execute multiple queries in a transaction
        
        Args:
            queries: List of (query, params) tuples
        
        Returns:
            True if successful, False otherwise
        """
        with self.get_connection() as conn:
            try:
                with conn.cursor() as cur:
                    for query, params in queries:
                        cur.execute(query, params or {})
                
                conn.commit()
                return True
                
            except Exception as e:
                conn.rollback()
                logger.error(f"Transaction failed: {e}")
                return False
    
    def close_all_connections(self):
        """Close all connections in pool"""
        if self.pool:
            self.pool.closeall()
            logger.info("Database pool closed")


# Singleton instance
db = DatabasePool()

