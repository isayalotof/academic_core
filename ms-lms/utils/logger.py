"""
Logging configuration for ms-lms
"""
import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_logger(
    name: str = 'ms-lms',
    level: str = 'INFO',
    json_format: bool = True
) -> logging.Logger:
    """Setup logger with JSON formatting"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers = []
    
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

