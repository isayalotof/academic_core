"""
Database Connection Pool
Управление пулом соединений PostgreSQL через psycopg2
"""

import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from typing import Optional, Any, List, Dict
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class Database:
    """Singleton для управления пулом соединений с PostgreSQL"""
    
    _instance: Optional['Database'] = None
    _pool: Optional[pool.ThreadedConnectionPool] = None
    
    def __new__(cls) -> 'Database':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._initialize_pool()
        return cls._instance
    
    @classmethod
    def _initialize_pool(cls) -> None:
        """Инициализация пула соединений"""
        try:
            cls._pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=int(os.getenv('DB_POOL_MIN', 5)),
                maxconn=int(os.getenv('DB_POOL_MAX', 20)),
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', 5432)),
                database=os.getenv('DB_NAME', 'university_db'),
                user=os.getenv('DB_USER', 'university_user'),
                password=os.getenv('DB_PASSWORD'),
                cursor_factory=RealDictCursor,
                connect_timeout=10
            )
            logger.info("Database connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    def get_connection(self):
        """Получить соединение из пула"""
        if self._pool is None:
            raise RuntimeError("Database pool not initialized")
        return self._pool.getconn()
    
    def return_connection(self, conn) -> None:
        """Вернуть соединение в пул"""
        if self._pool is None:
            raise RuntimeError("Database pool not initialized")
        self._pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, commit: bool = False):
        """
        Context manager для безопасной работы с курсором
        
        Args:
            commit: Автоматически коммитить транзакцию
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            yield cursor
            if commit:
                conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()
            self.return_connection(conn)
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[tuple] = None, 
        fetch: bool = True
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Выполнить SQL запрос
        
        Args:
            query: SQL запрос
            params: Параметры запроса
            fetch: Возвращать результаты (True для SELECT)
            
        Returns:
            Список словарей с результатами или None
        """
        with self.get_cursor(commit=not fetch) as cursor:
            cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            return None
    
    def execute_many(
        self, 
        query: str, 
        params_list: List[tuple]
    ) -> int:
        """
        Выполнить множественную вставку
        
        Args:
            query: SQL запрос
            params_list: Список параметров для каждой вставки
            
        Returns:
            Количество затронутых строк
        """
        with self.get_cursor(commit=True) as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    def close_all_connections(self) -> None:
        """Закрыть все соединения в пуле"""
        if self._pool:
            self._pool.closeall()
            logger.info("All database connections closed")


# Singleton instance
db = Database()

