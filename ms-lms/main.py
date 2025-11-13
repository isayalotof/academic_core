"""
ms-lms - Learning Management System
"""
import logging
import signal
import sys
import grpc
from concurrent import futures

from config import config
from utils.logger import setup_logger
from db.connection import get_pool, close_pool
from rpc.server import serve

logger = setup_logger(
    name='ms-lms',
    level=config.LOG_LEVEL,
    json_format=config.LOG_JSON
)


def shutdown_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("Shutdown signal received...")
    try:
        close_pool()
    except Exception as e:
        logger.error(f"Error closing database pool: {e}")
    logger.info("Shutdown complete")
    sys.exit(0)


def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("MS-LMS - Learning Management System")
    logger.info(f"Version: {config.SERVICE_VERSION}")
    logger.info(f"Environment: {config.ENVIRONMENT}")
    logger.info("=" * 60)
    
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    
    # Initialize database pool
    try:
        get_pool()
        logger.info("✓ Database pool initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize database: {e}")
        sys.exit(1)
    
    # Start gRPC server
    try:
        serve()
    except Exception as e:
        logger.error(f"✗ Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

