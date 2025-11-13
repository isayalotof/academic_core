"""
Database migration script for ms-core
Применяет SQL миграции в правильном порядке
"""
import os
import sys
import psycopg2
from psycopg2 import sql
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Подключение к БД
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'university_db')
DB_USER = os.getenv('DB_USER', 'university_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'university_pass_secure_2024')


def get_connection():
    """Создать подключение к БД"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        sys.exit(1)


def create_migrations_table(conn):
    """Создать таблицу для отслеживания миграций"""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS core_migrations (
                    id SERIAL PRIMARY KEY,
                    migration_name VARCHAR(255) UNIQUE NOT NULL,
                    applied_at TIMESTAMP DEFAULT NOW()
                )
            """)
        conn.commit()
        logger.info("✓ Migrations tracking table created")
    except Exception as e:
        logger.error(f"Failed to create migrations table: {e}")
        conn.rollback()
        raise


def get_applied_migrations(conn):
    """Получить список примененных миграций"""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT migration_name FROM core_migrations ORDER BY id")
            return set(row[0] for row in cur.fetchall())
    except Exception as e:
        logger.error(f"Failed to get applied migrations: {e}")
        return set()


def apply_migration(conn, migration_file, migration_name):
    """Применить одну миграцию"""
    try:
        # Прочитать SQL файл
        migration_path = os.path.join(os.path.dirname(__file__), migration_file)
        with open(migration_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Выполнить SQL
        with conn.cursor() as cur:
            cur.execute(sql_content)
            
            # Записать в таблицу миграций
            cur.execute(
                "INSERT INTO core_migrations (migration_name) VALUES (%s)",
                (migration_name,)
            )
        
        conn.commit()
        logger.info(f"✓ Applied migration: {migration_name}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to apply migration {migration_name}: {e}")
        conn.rollback()
        return False


def main():
    """Главная функция"""
    logger.info("=" * 60)
    logger.info("MS-CORE Database Migrations")
    logger.info("=" * 60)
    
    # Подключиться к БД
    conn = get_connection()
    logger.info(f"✓ Connected to database: {DB_NAME}@{DB_HOST}")
    
    # Создать таблицу миграций
    create_migrations_table(conn)
    
    # Получить примененные миграции
    applied = get_applied_migrations(conn)
    logger.info(f"Applied migrations: {len(applied)}")
    
    # Список миграций в правильном порядке
    migrations = [
        ('001_teachers.sql', '001_teachers'),
        ('002_preferences.sql', '002_preferences'),
        ('003_groups.sql', '003_groups'),
        ('004_students.sql', '004_students'),
        ('005_disciplines.sql', '005_disciplines'),
        ('006_course_loads.sql', '006_course_loads'),
        ('007_import_batches.sql', '007_import_batches'),
        ('008_update_semester_constraint.sql', '008_update_semester_constraint'),
        ('009_allow_null_teacher_id.sql', '009_allow_null_teacher_id'),
        ('010_update_lesson_type_constraint.sql', '010_update_lesson_type_constraint'),
    ]
    
    # Применить новые миграции
    applied_count = 0
    for migration_file, migration_name in migrations:
        if migration_name not in applied:
            logger.info(f"Applying: {migration_name}...")
            if apply_migration(conn, migration_file, migration_name):
                applied_count += 1
            else:
                logger.error("Migration failed! Stopping.")
                conn.close()
                sys.exit(1)
        else:
            logger.info(f"⊘ Skipping (already applied): {migration_name}")
    
    # Закрыть подключение
    conn.close()
    
    logger.info("=" * 60)
    if applied_count > 0:
        logger.info(f"✓ Successfully applied {applied_count} migration(s)")
    else:
        logger.info("✓ No new migrations to apply")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()

