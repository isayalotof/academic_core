"""
Database connection pool for ms-schedule
PostgreSQL connection management без ORM
"""

import psycopg2
from psycopg2 import pool, extras
from typing import Optional, Any, Dict, List
from contextlib import contextmanager
import logging

from config import config


logger = logging.getLogger(__name__)


class PostgreSQLConnectionPool:
    """PostgreSQL connection pool"""
    
    def __init__(self):
        """Initialize connection pool"""
        self._pool: Optional[pool.ThreadedConnectionPool] = None
        self._initialize_pool()
    
    def _initialize_pool(self) -> None:
        """Create connection pool"""
        try:
            self._pool = pool.ThreadedConnectionPool(
                minconn=config.DB_POOL_MIN,
                maxconn=config.DB_POOL_MAX,
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                cursor_factory=extras.RealDictCursor  # Return results as dicts
            )
            logger.info(
                f"✅ Database pool initialized: "
                f"{config.DB_POOL_MIN}-{config.DB_POOL_MAX} connections"
            )
        except psycopg2.Error as e:
            logger.error(f"❌ Failed to initialize connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Get connection from pool (context manager)
        
        Usage:
            with db_pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ...")
        """
        conn = None
        try:
            conn = self._pool.getconn()
            yield conn
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                self._pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, commit: bool = False):
        """
        Get cursor from pool (context manager)
        
        Args:
            commit: Auto-commit after successful execution
            
        Usage:
            with db_pool.get_cursor(commit=True) as cursor:
                cursor.execute("INSERT INTO ...")
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                if commit:
                    conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Query error: {e}")
                raise
            finally:
                cursor.close()
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[Dict[str, Any]] = None,
        fetch_one: bool = False,
        fetch_all: bool = True,
        commit: bool = False
    ) -> Optional[List[Dict] | Dict]:
        """
        Execute query and return results
        
        Args:
            query: SQL query
            params: Query parameters
            fetch_one: Return single row
            fetch_all: Return all rows
            commit: Commit transaction
            
        Returns:
            Query results as list of dicts or single dict
        """
        with self.get_cursor(commit=commit) as cursor:
            cursor.execute(query, params or {})
            
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            
            return None
    
    def execute_many(
        self,
        query: str,
        params_list: List[tuple],
        commit: bool = True
    ) -> int:
        """
        Execute query multiple times with different parameters
        
        Args:
            query: SQL query
            params_list: List of parameter tuples
            commit: Commit transaction
            
        Returns:
            Number of affected rows
        """
        with self.get_cursor(commit=commit) as cursor:
            extras.execute_batch(cursor, query, params_list)
            return cursor.rowcount
    
    def execute_values(
        self,
        query: str,
        values: List[tuple],
        template: Optional[str] = None,
        commit: bool = True
    ) -> List[Dict]:
        """
        Execute INSERT with multiple values (fast bulk insert)
        
        Args:
            query: SQL query with %s placeholder for values
            values: List of value tuples
            template: Optional template for values format
            commit: Commit transaction
            
        Returns:
            List of returned rows (if RETURNING clause)
        """
        with self.get_cursor(commit=commit) as cursor:
            result = extras.execute_values(
                cursor,
                query,
                values,
                template=template,
                fetch=True
            )
            return result if result else []
    
    def close(self) -> None:
        """Close all connections in pool"""
        if self._pool:
            self._pool.closeall()
            logger.info("Database pool closed")


# Global connection pool instance
db_pool: Optional[PostgreSQLConnectionPool] = None


def get_db_pool() -> PostgreSQLConnectionPool:
    """Get global database pool instance"""
    global db_pool
    if db_pool is None:
        db_pool = PostgreSQLConnectionPool()
    return db_pool


def close_db_pool() -> None:
    """Close global database pool"""
    global db_pool
    if db_pool:
        db_pool.close()
        db_pool = None

