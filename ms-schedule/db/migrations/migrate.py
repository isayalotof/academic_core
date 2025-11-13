"""
Database migration script for ms-schedule
Применение SQL миграций
"""

import psycopg2
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from config import config


def run_migrations():
    """Run all SQL migrations in order"""
    migrations_dir = Path(__file__).parent
    
    # Get all SQL files sorted by name
    migration_files = sorted(migrations_dir.glob('*.sql'))
    
    if not migration_files:
        print("⚠️  No migration files found!")
        return
    
    print(f"📦 Found {len(migration_files)} migration files")
    
    # Connect to database
    try:
        conn = psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
        conn.autocommit = False
        cursor = conn.cursor()
        
        print(f"✅ Connected to database: {config.DB_NAME}")
        
        # Create migrations tracking table (unique for ms-schedule)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedule_migrations (
                id SERIAL PRIMARY KEY,
                version VARCHAR(50) UNIQUE NOT NULL,
                filename VARCHAR(255) NOT NULL,
                applied_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        
        # Get already applied migrations
        cursor.execute("SELECT version FROM schedule_migrations")
        applied_migrations = {row[0] for row in cursor.fetchall()}
        
        # Apply each migration
        for migration_file in migration_files:
            filename = migration_file.name
            # Extract version from filename (e.g., "001_schedules.sql" -> "001")
            version = filename.split('_')[0]
            
            if version in applied_migrations:
                print(f"⏭️  Skipping {filename} (already applied)")
                continue
            
            print(f"🔄 Applying {filename}...", end=" ")
            
            try:
                # Read and execute migration
                with open(migration_file, 'r', encoding='utf-8') as f:
                    sql = f.read()
                
                cursor.execute(sql)
                
                # Record migration
                cursor.execute(
                    "INSERT INTO schedule_migrations (version, filename) VALUES (%s, %s)",
                    (version, filename)
                )
                
                conn.commit()
                print("✅")
                
            except Exception as e:
                conn.rollback()
                print(f"❌ Failed!")
                print(f"   Error: {str(e)}")
                raise
        
        print("\n🎉 All migrations applied successfully!")
        
        # Show summary
        cursor.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE tablename LIKE 'schedule%') as schedule_tables,
                COUNT(*) FILTER (WHERE tablename = 'schedules') as has_schedules,
                COUNT(*) FILTER (WHERE tablename = 'schedule_history') as has_history
            FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        
        stats = cursor.fetchone()
        print(f"\n📊 Database summary:")
        print(f"   Schedule tables: {stats[0]}")
        print(f"   Main table (schedules): {'✅' if stats[1] else '❌'}")
        print(f"   History tracking: {'✅' if stats[2] else '❌'}")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    print("=" * 60)
    print("MS-SCHEDULE DATABASE MIGRATIONS")
    print("=" * 60)
    print()
    
    run_migrations()

