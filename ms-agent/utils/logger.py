"""
Structured Logging
"""

import logging
import sys
from pythonjsonlogger import jsonlogger
import os


def setup_logger(name: str = 'ms-agent') -> logging.Logger:
    """Setup structured logger"""
    logger = logging.getLogger(name)
    
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logger.setLevel(getattr(logging, log_level))
    
    logger.handlers.clear()
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level))
    
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
    logger.propagate = False
    
    return logger


logger = setup_logger()

