"""
ms-core - Микросервис базовых сущностей
Управление преподавателями, группами, студентами и учебной нагрузкой
"""
import logging
import os
import signal
import sys
from concurrent import futures
import grpc

# Импорты конфигурации и утилит
from config import config
from utils.logger import setup_logger
from db.connection import get_pool, close_pool
from utils.cache import get_cache
from rpc.server import serve

# Setup logger
logger = setup_logger(
    name='ms-core',
    level=config.LOG_LEVEL,
    json_format=config.LOG_JSON
)


def shutdown_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("Shutdown signal received...")
    
    # Close database pool
    try:
        close_pool()
    except Exception as e:
        logger.error(f"Error closing database pool: {e}")
    
    logger.info("Shutdown complete")
    sys.exit(0)


def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("MS-CORE - University Core Entities Management")
    logger.info(f"Version: {config.SERVICE_VERSION}")
    logger.info(f"Environment: {config.ENVIRONMENT}")
    logger.info("=" * 60)
    
    # Validate configuration
    try:
        config.validate()
        logger.info("✓ Configuration validated")
    except ValueError as e:
        logger.error(f"✗ Configuration error: {e}")
        sys.exit(1)
    
    # Initialize database pool
    try:
        db_pool = get_pool()
        logger.info(f"✓ Database pool initialized: {config.DB_NAME}@{config.DB_HOST}")
    except Exception as e:
        logger.error(f"✗ Failed to initialize database pool: {e}")
        sys.exit(1)
    
    # Run database migrations
    if os.getenv('SKIP_MIGRATIONS', '').lower() != 'true':
        try:
            from db.migrations.migrate import main as run_migrations
            logger.info("Running database migrations...")
            run_migrations()
            logger.info("✓ Migrations completed")
        except Exception as e:
            logger.warning(f"⚠ Migration error (continuing anyway): {e}")
    else:
        logger.info("Skipping migrations (SKIP_MIGRATIONS=true)")
    
    # Initialize Redis cache
    try:
        cache = get_cache()
        if cache.client:
            logger.info(f"✓ Redis cache initialized: {config.REDIS_HOST}:{config.REDIS_PORT}")
        else:
            logger.warning("⚠ Redis cache not available (running without cache)")
    except Exception as e:
        logger.warning(f"⚠ Redis cache initialization failed: {e}")
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    
    # Start gRPC server
    logger.info(f"Starting gRPC server on port {config.GRPC_PORT}...")
    try:
        serve()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

