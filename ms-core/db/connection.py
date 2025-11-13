"""
PostgreSQL connection pool for ms-core
БЕЗ ORM - только чистый psycopg2
"""
import psycopg2
from psycopg2 import pool
import logging
from typing import Optional
import os

logger = logging.getLogger(__name__)


class PostgreSQLConnectionPool:
    """Пул соединений PostgreSQL"""
    
    def __init__(
        self,
        minconn: int = 2,
        maxconn: int = 10,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Инициализация пула соединений
        
        Args:
            minconn: Минимальное количество соединений
            maxconn: Максимальное количество соединений
            host: Хост БД (или из env)
            port: Порт БД (или из env)
            database: Имя БД (или из env)
            user: Пользователь (или из env)
            password: Пароль (или из env)
        """
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.port = port or int(os.getenv('DB_PORT', 5432))
        self.database = database or os.getenv('DB_NAME', 'university_db')
        self.user = user or os.getenv('DB_USER', 'university_user')
        self.password = password or os.getenv('DB_PASSWORD', 'university_pass')
        
        try:
            self.pool = psycopg2.pool.ThreadedConnectionPool(
                minconn,
                maxconn,
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            logger.info(f"✓ Connection pool created: {self.database}@{self.host}")
        except Exception as e:
            logger.error(f"✗ Failed to create connection pool: {e}")
            raise
    
    def get_connection(self):
        """Получить соединение из пула"""
        try:
            conn = self.pool.getconn()
            return conn
        except Exception as e:
            logger.error(f"Error getting connection from pool: {e}")
            raise
    
    def return_connection(self, conn):
        """Вернуть соединение в пул"""
        try:
            self.pool.putconn(conn)
        except Exception as e:
            logger.error(f"Error returning connection to pool: {e}")
            raise
    
    def close_all_connections(self):
        """Закрыть все соединения в пуле"""
        try:
            self.pool.closeall()
            logger.info("✓ All connections closed")
        except Exception as e:
            logger.error(f"Error closing connections: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        """
        Выполнить SQL запрос
        
        Args:
            query: SQL запрос
            params: Параметры запроса
            fetch: Вернуть результаты (True) или только выполнить (False)
        
        Returns:
            Результаты запроса если fetch=True, иначе None
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                
                if fetch:
                    # Вернуть все строки
                    columns = [desc[0] for desc in cur.description] if cur.description else []
                    rows = cur.fetchall()
                    
                    # Преобразовать в список словарей
                    result = []
                    for row in rows:
                        result.append(dict(zip(columns, row)))
                    
                    return result
                else:
                    conn.commit()
                    return None
        except Exception as e:
            conn.rollback()
            logger.error(f"Query execution error: {e}")
            raise
        finally:
            self.return_connection(conn)


# Глобальный пул соединений
_connection_pool: Optional[PostgreSQLConnectionPool] = None


def get_pool() -> PostgreSQLConnectionPool:
    """Получить глобальный пул соединений"""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = PostgreSQLConnectionPool()
    return _connection_pool


def close_pool():
    """Закрыть глобальный пул соединений"""
    global _connection_pool
    if _connection_pool is not None:
        _connection_pool.close_all_connections()
        _connection_pool = None

