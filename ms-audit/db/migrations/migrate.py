#!/usr/bin/env python3
"""
Database Migration Script
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


def check_table_exists(conn, table_name: str) -> bool:
    """Проверить существование таблицы"""
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            )
        """, (table_name,))
        return cursor.fetchone()[0]


def run_migrations() -> int:
    """Запустить все непримененные миграции"""
    logger.info("Starting database migrations...")
    
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
        
        # Проверка целостности: если миграция применена, но таблицы нет - переприменить
        # Ключевые таблицы для проверки
        critical_tables = {
            '001': ['buildings', 'classrooms', 'classroom_schedules'],
            '002': []  # Индексы не требуют проверки
        }
        
        # Список миграций для переприменения (без дубликатов)
        migrations_to_reapply = []
        reapply_versions = set()  # Для отслеживания уже добавленных версий
        
        for version, file_path in migration_files:
            if version in applied and version not in reapply_versions:
                # Проверить существование критических таблиц
                if version in critical_tables:
                    for table_name in critical_tables[version]:
                        if not check_table_exists(conn, table_name):
                            logger.warning(
                                f"Migration {version} is marked as applied, "
                                f"but table '{table_name}' does not exist. "
                                f"Will re-apply migration..."
                            )
                            # Удалить запись о применении
                            with conn.cursor() as cursor:
                                cursor.execute(
                                    "DELETE FROM schema_migrations WHERE version = %s",
                                    (version,)
                                )
                                conn.commit()
                            # Добавить в список для переприменения
                            migrations_to_reapply.append((version, file_path))
                            reapply_versions.add(version)
                            # Удалить из списка примененных
                            applied.discard(version)
                            break  # Достаточно одной отсутствующей таблицы
        
        # Применить миграции, которые нужно переприменить
        for version, file_path in migrations_to_reapply:
            if apply_migration(conn, version, file_path):
                logger.info(f"✓ Re-applied migration {version}")
            else:
                logger.error(f"Failed to re-apply migration {version}")
                conn.close()
                return 1
        
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

