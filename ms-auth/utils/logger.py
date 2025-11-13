"""
Structured Logging Configuration
Настройка структурированного логирования для микросервиса
"""

import logging
import sys
from pythonjsonlogger import jsonlogger
import os


def setup_logger(name: str = 'ms-auth') -> logging.Logger:
    """
    Настроить структурированный logger с JSON форматом
    
    Args:
        name: Имя логгера
        
    Returns:
        Настроенный logger
    """
    logger = logging.getLogger(name)
    
    # Set log level from environment
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logger.setLevel(getattr(logging, log_level))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level))
    
    # JSON formatter
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
        rename_fields={
            'asctime': 'timestamp',
            'levelname': 'level',
            'name': 'logger'
        }
    )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


# Create default logger instance
logger = setup_logger()

