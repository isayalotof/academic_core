"""
Migration script for ms-cafeteria
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
            cur.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version VARCHAR(255) PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cur.execute("SELECT version FROM schema_migrations")
            applied = {row[0] for row in cur.fetchall()}
            
            migrations_dir = os.path.join(os.path.dirname(__file__))
            migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])
            
            for migration_file in migration_files:
                version = migration_file.replace('.sql', '')
                if version in applied:
                    logger.info(f"Migration {version} already applied, skipping")
                    continue
                
                logger.info(f"Applying migration {version}...")
                migration_path = os.path.join(migrations_dir, migration_file)
                
                with open(migration_path, 'r', encoding='utf-8') as f:
                    sql = f.read()
                
                cur.execute(sql)
                cur.execute("INSERT INTO schema_migrations (version) VALUES (%s)", (version,))
                conn.commit()
                logger.info(f"✓ Migration {version} applied successfully")
            
            logger.info("All migrations completed")
    finally:
        pool.return_connection(conn)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_migrations()

