"""
PostgreSQL connection pool for ms-documents
"""
import psycopg2
from psycopg2 import pool
import logging
from typing import Optional
import os

logger = logging.getLogger(__name__)


class PostgreSQLConnectionPool:
    def __init__(self, minconn: int = 2, maxconn: int = 10, host: Optional[str] = None,
                 port: Optional[int] = None, database: Optional[str] = None,
                 user: Optional[str] = None, password: Optional[str] = None):
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.port = port or int(os.getenv('DB_PORT', 5432))
        self.database = database or os.getenv('DB_NAME', 'university_db')
        self.user = user or os.getenv('DB_USER', 'university_user')
        self.password = password or os.getenv('DB_PASSWORD', 'university_pass')
        
        try:
            self.pool = psycopg2.pool.ThreadedConnectionPool(
                minconn, maxconn, host=self.host, port=self.port,
                database=self.database, user=self.user, password=self.password
            )
            logger.info(f"✓ Connection pool created: {self.database}@{self.host}")
        except Exception as e:
            logger.error(f"✗ Failed to create connection pool: {e}")
            raise
    
    def get_connection(self):
        return self.pool.getconn()
    
    def return_connection(self, conn):
        self.pool.putconn(conn)
    
    def close_all_connections(self):
        self.pool.closeall()
        logger.info("✓ All connections closed")


_connection_pool: Optional[PostgreSQLConnectionPool] = None


def get_pool() -> PostgreSQLConnectionPool:
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = PostgreSQLConnectionPool()
    return _connection_pool


def close_pool():
    global _connection_pool
    if _connection_pool is not None:
        _connection_pool.close_all_connections()
        _connection_pool = None

