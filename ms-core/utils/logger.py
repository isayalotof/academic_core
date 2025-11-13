"""
Centralized logging configuration for ms-core
Structured JSON logging
"""
import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data: Dict[str, Any] = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_logger(
    name: str = 'ms-core',
    level: str = 'INFO',
    json_format: bool = True
) -> logging.Logger:
    """
    Setup logger with JSON formatting
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON formatting
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    
    if json_format:
        handler.setFormatter(JSONFormatter())
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


# Global logger instance
logger = setup_logger()


def get_logger(name: str = None) -> logging.Logger:
    """
    Get logger instance
    
    Args:
        name: Logger name (optional)
    
    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f'ms-core.{name}')
    return logger

