"""
GigaChat API Client
Клиент для работы с GigaChat API от Сбер
OAuth 2.0 + Chat Completions + Functions
"""

import requests
import uuid
import time
import logging
from typing import List, Dict, Any, Optional
import base64
import json
import urllib3

from config import config

# Отключаем предупреждения SSL для корпоративных сертификатов
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class GigaChatClient:
    """Клиент для работы с GigaChat API"""
    
    BASE_URL = "https://gigachat.devices.sberbank.ru/api/v1"
    TOKEN_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    
    def __init__(self):
        """Initialize GigaChat client"""
        self.client_id = config.GIGACHAT_CLIENT_ID
        self.client_secret = config.GIGACHAT_CLIENT_SECRET
        self.scope = config.GIGACHAT_SCOPE
        
        self.access_token: Optional[str] = None
        self.token_expires_at: int = 0
        
        if not self.client_id or not self.client_secret:
            logger.warning("⚠️ GigaChat credentials not configured")
        else:
            self._ensure_token()
    
    def _get_auth_header(self) -> str:
        """Получить Authorization header для получения токена"""
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    
    def _ensure_token(self):
        """Проверить токен и обновить если истёк"""
        current_time = int(time.time())
        
        # Обновить за 5 минут до истечения
        if self.access_token and current_time < (self.token_expires_at - 300):
            return
        
        logger.info("🔄 Refreshing GigaChat access token...")
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': str(uuid.uuid4()),
            'Authorization': self._get_auth_header()
        }
        
        data = {'scope': self.scope}
        
        try:
            response = requests.post(
                self.TOKEN_URL,
                headers=headers,
                data=data,
                verify=False,  # Отключаем проверку SSL для корпоративных сертификатов
                timeout=10
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            self.token_expires_at = token_data['expires_at']
            
            logger.info(f"✅ GigaChat token obtained, expires at {self.token_expires_at}")
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Failed to get GigaChat token: {e.response.text if e.response else e}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to get GigaChat token: {e}")
            raise
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        functions: Optional[List[Dict]] = None,
        function_call: str = "auto",
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Запрос к GigaChat Chat Completions
        
        Args:
            messages: Список сообщений [{"role": "user", "content": "..."}]
            functions: Описание функций для агента
            function_call: "auto" или "none"
            model: "GigaChat", "GigaChat-Plus", "GigaChat-Pro"
            temperature: 0.0-2.0
            max_tokens: Максимум токенов в ответе
            stream: Потоковая передача
        
        Returns:
            Ответ от API
        """
        self._ensure_token()
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        
        payload = {
            'model': model or config.GIGACHAT_MODEL,
            'messages': messages,
            'temperature': temperature if temperature is not None else config.GIGACHAT_TEMPERATURE,
            'max_tokens': max_tokens or config.GIGACHAT_MAX_TOKENS,
            'stream': stream
        }
        
        # Добавить функции если есть
        if functions:
            payload['functions'] = functions
            payload['function_call'] = function_call
        
        try:
            logger.debug(f"🤖 GigaChat request: {len(messages)} messages, functions: {bool(functions)}")
            
            response = requests.post(
                f'{self.BASE_URL}/chat/completions',
                headers=headers,
                json=payload,
                verify=False,  # Отключаем проверку SSL для корпоративных сертификатов
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            logger.debug(f"✅ GigaChat response received")
            
            return result
            
        except requests.exceptions.HTTPError as e:
            error_text = e.response.text if e.response else str(e)
            logger.error(f"❌ GigaChat API error: {error_text}")
            raise
        except Exception as e:
            logger.error(f"❌ GigaChat request failed: {e}")
            raise
    
    def get_available_models(self) -> List[Dict]:
        """Получить список доступных моделей"""
        self._ensure_token()
        
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        
        try:
            response = requests.get(
                f'{self.BASE_URL}/models',
                headers=headers,
                verify=True,
                timeout=10
            )
            response.raise_for_status()
            return response.json()['data']
            
        except Exception as e:
            logger.error(f"❌ Failed to get models: {e}")
            raise
    
    def call_with_tools(
        self,
        system_prompt: str,
        user_message: str,
        tools: List[Dict],
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Удобный метод для вызова с инструментами
        
        Args:
            system_prompt: Системный промпт
            user_message: Сообщение пользователя
            tools: Список определений инструментов
            conversation_history: История разговора
        
        Returns:
            Ответ с функцией или текстом
        """
        messages = []
        
        # Системный промпт
        messages.append({
            'role': 'system',
            'content': system_prompt
        })
        
        # История (если есть)
        if conversation_history:
            messages.extend(conversation_history)
        
        # Текущее сообщение
        messages.append({
            'role': 'user',
            'content': user_message
        })
        
        response = self.chat_completion(
            messages=messages,
            functions=tools,
            function_call="auto"
        )
        
        return self._parse_response(response)
    
    def _parse_response(self, response: Dict) -> Dict[str, Any]:
        """
        Распарсить ответ от GigaChat
        
        Returns:
            {
                'type': 'function_call' или 'text',
                'function_name': str,  # если type == 'function_call'
                'arguments': dict,     # если type == 'function_call'
                'content': str,        # если type == 'text'
                'reasoning': str       # если есть
            }
        """
        try:
            choice = response['choices'][0]
            message = choice['message']
            
            # Проверить, есть ли function_call
            if 'function_call' in message:
                func_call = message['function_call']
                
                # Парсинг аргументов (могут быть строкой или dict)
                arguments = func_call.get('arguments', '{}')
                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse function arguments: {arguments}")
                        arguments = {}
                
                return {
                    'type': 'function_call',
                    'function_name': func_call['name'],
                    'arguments': arguments,
                    'reasoning': message.get('content', '')
                }
            
            # Обычный текстовый ответ
            return {
                'type': 'text',
                'content': message.get('content', ''),
                'reasoning': message.get('content', '')
            }
            
        except Exception as e:
            logger.error(f"Failed to parse GigaChat response: {e}")
            logger.error(f"Response: {response}")
            raise
    
    def continue_conversation(
        self,
        messages: List[Dict],
        function_result: Dict,
        tools: List[Dict]
    ) -> Dict[str, Any]:
        """
        Продолжить разговор после выполнения функции
        
        Args:
            messages: История сообщений
            function_result: Результат выполнения функции
            tools: Список инструментов
        
        Returns:
            Следующий ответ агента
        """
        # Добавить результат функции
        messages.append({
            'role': 'function',
            'name': function_result['function_name'],
            'content': json.dumps(function_result['result'], ensure_ascii=False)
        })
        
        response = self.chat_completion(
            messages=messages,
            functions=tools,
            function_call="auto"
        )
        
        return self._parse_response(response)


# Singleton instance
gigachat_client = GigaChatClient()

