#!/usr/bin/env python3
"""
MS-Agent Main Entry Point
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import setup_logger
from config import config
from db.connection import db

logger = setup_logger('ms-agent')


def check_database_connection():
    """Check database connection"""
    try:
        result = db.execute_query("SELECT 1", fetch=True)
        if result:
            logger.info("✓ Database connection successful")
            return True
        else:
            logger.error("✗ Database connection failed")
            return False
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        return False


def check_configuration():
    """Check configuration"""
    logger.info("Checking configuration...")
    logger.info(f"Environment: {config.ENVIRONMENT}")
    logger.info(f"gRPC Port: {config.GRPC_PORT}")
    logger.info(f"Database: {config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}")
    logger.info(f"GigaChat Model: {config.GIGACHAT_MODEL}")
    
    if config.ENVIRONMENT == 'production' and not config.validate():
        logger.error("✗ Configuration validation failed")
        return False
    
    logger.info("✓ Configuration valid")
    return True


def run_migrations():
    """Run database migrations"""
    logger.info("Checking database migrations...")
    
    try:
        from db.migrations.migrate import run_migrations
        result = run_migrations()
        
        if result == 0:
            logger.info("✓ Migrations applied successfully")
            return True
        else:
            logger.error("✗ Migration failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ Migration error: {e}")
        return False


def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("MS-AGENT - LLM Schedule Optimization Agent")
    logger.info(f"Version: {config.SERVICE_VERSION}")
    logger.info("=" * 60)
    
    if not check_configuration():
        logger.error("Configuration check failed. Exiting.")
        sys.exit(1)
    
    if not check_database_connection():
        logger.error("Database connection check failed. Exiting.")
        sys.exit(1)
    
    if os.getenv('SKIP_MIGRATIONS', '').lower() != 'true':
        if not run_migrations():
            logger.warning("Migrations failed, but continuing anyway...")
    else:
        logger.info("Skipping migrations (SKIP_MIGRATIONS=true)")
    
    try:
        from rpc.server import serve
        
        logger.info("Starting gRPC server...")
        serve()
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
        
    finally:
        logger.info("Cleaning up...")
        db.close_all_connections()
        logger.info("Shutdown complete")


if __name__ == '__main__':
    main()

