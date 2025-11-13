#!/usr/bin/env python3
"""
MS-Auth Main Entry Point
Главная точка входа для микросервиса аутентификации
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import setup_logger
from config import config
from db.connection import db

# Setup logging
logger = setup_logger('ms-auth')


def check_database_connection():
    """Проверить соединение с базой данных"""
    try:
        result = db.execute_query("SELECT 1", fetch=True)
        if result:
            logger.info("✓ Database connection successful")
            return True
        else:
            logger.error("✗ Database connection failed: No result")
            return False
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        return False


def check_configuration():
    """Проверить конфигурацию"""
    logger.info("Checking configuration...")
    logger.info(f"Environment: {config.ENVIRONMENT}")
    logger.info(f"gRPC Port: {config.GRPC_PORT}")
    logger.info(f"Database: {config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}")
    logger.info(f"Redis: {config.REDIS_HOST}:{config.REDIS_PORT}")
    logger.info(f"JWT Access Token Expire: {config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    logger.info(f"JWT Refresh Token Expire: {config.JWT_REFRESH_TOKEN_EXPIRE_DAYS} days")
    logger.info(f"Bcrypt Rounds: {config.BCRYPT_ROUNDS}")
    logger.info(f"Max Login Attempts: {config.MAX_LOGIN_ATTEMPTS}")
    
    if config.ENVIRONMENT == 'production' and not config.validate():
        logger.error("✗ Configuration validation failed")
        logger.error("Please ensure all required passwords and secrets are set")
        return False
    
    logger.info("✓ Configuration valid")
    return True


def run_migrations():
    """Применить миграции базы данных"""
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
    logger.info("MS-AUTH - Authentication & Authorization Microservice")
    logger.info(f"Version: {config.SERVICE_VERSION}")
    logger.info("=" * 60)
    
    # Check configuration
    if not check_configuration():
        logger.error("Configuration check failed. Exiting.")
        sys.exit(1)
    
    # Check database connection
    if not check_database_connection():
        logger.error("Database connection check failed. Exiting.")
        sys.exit(1)
    
    # Run migrations
    if os.getenv('SKIP_MIGRATIONS', '').lower() != 'true':
        if not run_migrations():
            logger.warning("Migrations failed, but continuing anyway...")
    else:
        logger.info("Skipping migrations (SKIP_MIGRATIONS=true)")
    
    # Start gRPC server
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
        # Cleanup
        logger.info("Cleaning up...")
        db.close_all_connections()
        logger.info("Shutdown complete")


if __name__ == '__main__':
    main()

