#!/usr/bin/env python3
"""
Database migrations runner
Применяет SQL миграции для ms-agent
"""

import os
import sys
from pathlib import Path
import psycopg2
import logging

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_connection():
    """Get database connection"""
    return psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        database=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD
    )


def create_migrations_table(conn):
    """Create migrations tracking table"""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS agent_migrations (
                id SERIAL PRIMARY KEY,
                migration_name VARCHAR(255) UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        logger.info("Migrations table created/verified")


def get_applied_migrations(conn):
    """Get list of applied migrations"""
    with conn.cursor() as cur:
        cur.execute("SELECT migration_name FROM agent_migrations ORDER BY id")
        return {row[0] for row in cur.fetchall()}


def apply_migration(conn, migration_file: Path):
    """Apply single migration"""
    migration_name = migration_file.name
    
    logger.info(f"Applying migration: {migration_name}")
    
    try:
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        with conn.cursor() as cur:
            cur.execute(sql)
            cur.execute(
                "INSERT INTO agent_migrations (migration_name) VALUES (%s)",
                (migration_name,)
            )
        
        conn.commit()
        logger.info(f"✓ Migration {migration_name} applied successfully")
        return True
        
    except Exception as e:
        conn.rollback()
        logger.error(f"✗ Failed to apply {migration_name}: {e}")
        return False


def run_migrations():
    """Run all pending migrations"""
    migrations_dir = Path(__file__).parent
    
    # Get all .sql files sorted by name
    migration_files = sorted(migrations_dir.glob('*.sql'))
    
    if not migration_files:
        logger.warning("No migration files found")
        return 0
    
    logger.info(f"Found {len(migration_files)} migration files")
    
    try:
        conn = get_connection()
        logger.info("✓ Connected to database")
        
        # Create migrations table
        create_migrations_table(conn)
        
        # Get applied migrations
        applied = get_applied_migrations(conn)
        logger.info(f"Already applied: {len(applied)} migrations")
        
        # Apply pending migrations
        pending = [f for f in migration_files if f.name not in applied]
        
        if not pending:
            logger.info("✓ All migrations already applied")
            return 0
        
        logger.info(f"Pending migrations: {len(pending)}")
        
        success_count = 0
        for migration_file in pending:
            if apply_migration(conn, migration_file):
                success_count += 1
            else:
                logger.error(f"Migration failed, stopping")
                return 1
        
        logger.info(f"✓ Successfully applied {success_count} migrations")
        return 0
        
    except psycopg2.Error as e:
        logger.error(f"✗ Database error: {e}")
        return 1
    except Exception as e:
        logger.error(f"✗ Unexpected error: {e}")
        return 1
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == '__main__':
    sys.exit(run_migrations())

