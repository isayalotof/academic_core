"""
Centralized logging configuration for ms-schedule
Структурированное логирование
"""

import logging
import sys
from pythonjsonlogger import jsonlogger
from config import config


def setup_logging() -> logging.Logger:
    """Setup structured logging"""
    
    # Create logger
    logger = logging.getLogger('ms-schedule')
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    
    # JSON formatter
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        rename_fields={
            'asctime': 'timestamp',
            'levelname': 'level',
            'name': 'service'
        }
    )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    logger.info(
        "Logging initialized",
        extra={
            'service': config.SERVICE_NAME,
            'version': config.SERVICE_VERSION,
            'environment': config.ENVIRONMENT,
            'log_level': config.LOG_LEVEL
        }
    )
    
    return logger


# Global logger instance
logger = setup_logging()

