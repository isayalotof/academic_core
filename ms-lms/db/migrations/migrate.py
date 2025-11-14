"""
Migration script for ms-lms
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from db.connection import get_pool
import logging

logger = logging.getLogger(__name__)


def run_migrations():
    """Run all migrations"""
    pool = get_pool()
    conn = pool.get_connection()
    
    try:
        with conn.cursor() as cur:
            # Create migrations table if not exists (совместимо с существующей структурой)
            # Проверить существующую структуру таблицы
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'schema_migrations'
                ORDER BY ordinal_position
            """)
            existing_columns = {row[0] for row in cur.fetchall()}
            
            # Создать таблицу с правильной структурой
            if not existing_columns:
                # Таблица не существует - создаём с полной структурой
                cur.execute("""
                    CREATE TABLE schema_migrations (
                        id SERIAL PRIMARY KEY,
                        version VARCHAR(255) UNIQUE NOT NULL,
                        filename VARCHAR(255) NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
            elif 'filename' not in existing_columns:
                # Таблица существует, но без filename - добавить колонку
                cur.execute("""
                    ALTER TABLE schema_migrations 
                    ADD COLUMN filename VARCHAR(255) NOT NULL DEFAULT ''
                """)
                conn.commit()
                logger.info("Added filename column to existing schema_migrations table")
                existing_columns.add('filename')  # Обновить для дальнейших проверок
            
            # Очистить некорректные записи (с NULL filename) если они есть
            if 'filename' in existing_columns:
                cur.execute("""
                    DELETE FROM schema_migrations 
                    WHERE filename IS NULL
                """)
                if cur.rowcount > 0:
                    conn.commit()
                    logger.info(f"Cleaned up {cur.rowcount} invalid migration records")
            
            # Get applied migrations
            cur.execute("SELECT version FROM schema_migrations")
            applied = {row[0] for row in cur.fetchall()}
            
            # Run migrations in order
            migrations_dir = os.path.dirname(__file__)
            migration_files = sorted([
                f for f in os.listdir(migrations_dir)
                if f.endswith('.sql') and f != 'migrate.py'
            ])
            
            for migration_file in migration_files:
                version = migration_file.replace('.sql', '')
                if version in applied:
                    logger.info(f"Migration {version} already applied, skipping")
                    continue
                
                # Проверить, может быть таблицы уже созданы (миграция была применена вручную)
                # Для 001_create_lms_tables проверяем наличие таблицы courses
                if version == '001_create_lms_tables':
                    cur.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'courses'
                        )
                    """)
                    if cur.fetchone()[0]:
                        logger.info(f"Tables from {version} already exist, marking as applied")
                        cur.execute(
                            "INSERT INTO schema_migrations (version, filename) VALUES (%s, %s) ON CONFLICT (version) DO NOTHING",
                            (version, migration_file)
                        )
                        conn.commit()
                        continue
                
                logger.info(f"Applying migration {version}...")
                migration_path = os.path.join(migrations_dir, migration_file)
                
                try:
                    with open(migration_path, 'r', encoding='utf-8') as f:
                        sql = f.read()
                    
                    # Execute migration
                    cur.execute(sql)
                    
                    # Insert migration record (всегда с filename)
                    cur.execute(
                        "INSERT INTO schema_migrations (version, filename) VALUES (%s, %s) ON CONFLICT (version) DO NOTHING",
                        (version, migration_file)
                    )
                    
                    conn.commit()
                    logger.info(f"✓ Migration {version} applied successfully")
                except Exception as e:
                    conn.rollback()
                    logger.error(f"✗ Failed to apply migration {version}: {e}")
                    raise
            
            logger.info("All migrations completed")
    finally:
        pool.return_connection(conn)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_migrations()

