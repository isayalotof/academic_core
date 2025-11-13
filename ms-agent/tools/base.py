"""
Base Tool class
Базовый класс для инструментов агента
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class Tool(ABC):
    """Базовый класс для инструмента агента"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def get_definition(self) -> Dict[str, Any]:
        """
        Получить определение инструмента для GigaChat Functions API
        
        Returns:
            {
                "name": str,
                "description": str,
                "parameters": {...}
            }
        """
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Выполнить инструмент
        
        Args:
            **kwargs: Параметры из LLM
        
        Returns:
            Результат выполнения
        """
        pass
    
    def __call__(self, **kwargs) -> Dict[str, Any]:
        """Alias для execute"""
        try:
            logger.debug(f"🔧 Tool {self.name} executing with params: {kwargs}")
            result = self.execute(**kwargs)
            logger.debug(f"✅ Tool {self.name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"❌ Tool {self.name} failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

