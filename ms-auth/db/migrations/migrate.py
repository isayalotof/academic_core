#!/usr/bin/env python3
"""
Database Migration Script для ms-auth
Применяет SQL миграции к базе данных
"""

import os
import sys
import psycopg2
from pathlib import Path
from typing import List, Tuple
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_db_connection():
    """Создать соединение с БД из переменных окружения"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', 5432),
            database=os.getenv('DB_NAME', 'university_db'),
            user=os.getenv('DB_USER', 'university_user'),
            password=os.getenv('DB_PASSWORD')
        )
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


def create_migrations_table(conn) -> None:
    """Создать таблицу для отслеживания применённых миграций"""
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                version VARCHAR(50) UNIQUE NOT NULL,
                filename VARCHAR(255) NOT NULL,
                applied_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        logger.info("Migrations table created or already exists")


def get_applied_migrations(conn) -> set:
    """Получить список уже применённых миграций"""
    with conn.cursor() as cursor:
        cursor.execute("SELECT version FROM schema_migrations ORDER BY version")
        return {row[0] for row in cursor.fetchall()}


def get_migration_files() -> List[Tuple[str, Path]]:
    """Получить список файлов миграций"""
    migrations_dir = Path(__file__).parent
    migration_files = []
    
    for file_path in sorted(migrations_dir.glob('*.sql')):
        version = file_path.stem.split('_')[0]
        migration_files.append((version, file_path))
    
    return migration_files


def apply_migration(conn, version: str, file_path: Path) -> bool:
    """Применить одну миграцию"""
    try:
        logger.info(f"Applying migration {version}: {file_path.name}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        with conn.cursor() as cursor:
            # Execute migration SQL
            cursor.execute(sql)
            
            # Record migration
            cursor.execute(
                "INSERT INTO schema_migrations (version, filename) VALUES (%s, %s)",
                (version, file_path.name)
            )
            
            conn.commit()
            logger.info(f"✓ Migration {version} applied successfully")
            return True
            
    except Exception as e:
        conn.rollback()
        logger.error(f"✗ Failed to apply migration {version}: {e}")
        return False


def run_migrations() -> int:
    """Запустить все непримененные миграции"""
    logger.info("Starting database migrations for ms-auth...")
    
    try:
        # Connect to database
        conn = get_db_connection()
        logger.info("Connected to database")
        
        # Create migrations tracking table
        create_migrations_table(conn)
        
        # Get applied migrations
        applied = get_applied_migrations(conn)
        logger.info(f"Found {len(applied)} already applied migration(s)")
        
        # Get migration files
        migration_files = get_migration_files()
        logger.info(f"Found {len(migration_files)} total migration file(s)")
        
        # Apply pending migrations
        pending_count = 0
        success_count = 0
        
        for version, file_path in migration_files:
            if version not in applied:
                pending_count += 1
                if apply_migration(conn, version, file_path):
                    success_count += 1
                else:
                    logger.error("Migration failed, stopping")
                    conn.close()
                    return 1
        
        if pending_count == 0:
            logger.info("No pending migrations")
        else:
            logger.info(f"Successfully applied {success_count}/{pending_count} migration(s)")
        
        conn.close()
        logger.info("Migrations completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Migration process failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(run_migrations())

