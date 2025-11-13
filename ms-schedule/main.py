"""
Main entry point for ms-schedule
Точка входа для микросервиса расписания
"""

import sys
import signal
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from utils.logger import logger
from db.connection import get_db_pool, close_db_pool
from utils.cache import cache
from rpc.server import serve


def run_migrations():
    """Run database migrations"""
    logger.info("Running database migrations...")
    
    try:
        from db.migrations.migrate import run_migrations as apply_migrations
        apply_migrations()
        logger.info("✅ Migrations completed")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        sys.exit(1)


def shutdown_handler(signum, frame):
    """Graceful shutdown handler"""
    logger.info("Shutdown signal received, cleaning up...")
    
    # Close database connections
    close_db_pool()
    
    # Close cache connection
    cache.close()
    
    logger.info("Shutdown complete")
    sys.exit(0)


def main():
    """Main function"""
    logger.info("=" * 60)
    logger.info(f"STARTING {config.SERVICE_NAME.upper()}")
    logger.info("=" * 60)
    
    logger.info(f"Version: {config.SERVICE_VERSION}")
    logger.info(f"Environment: {config.ENVIRONMENT}")
    logger.info(f"gRPC Port: {config.GRPC_PORT}")
    logger.info(f"Database: {config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}")
    logger.info(f"Redis: {config.REDIS_HOST}:{config.REDIS_PORT}")
    logger.info(f"Cache Enabled: {config.CACHE_ENABLED}")
    logger.info(f"Log Level: {config.LOG_LEVEL}")
    
    # Validate configuration
    if not config.validate():
        logger.error("❌ Configuration validation failed!")
        sys.exit(1)
    
    logger.info("✅ Configuration validated")
    
    # Initialize database pool
    try:
        db_pool = get_db_pool()
        logger.info("✅ Database connection pool initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        sys.exit(1)
    
    # Run migrations
    if not config.ENVIRONMENT.startswith('test'):
        run_migrations()
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    
    logger.info("")
    logger.info("🚀 Starting gRPC server...")
    logger.info("")
    
    # Start server (blocking)
    try:
        serve()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received")
        shutdown_handler(None, None)
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

