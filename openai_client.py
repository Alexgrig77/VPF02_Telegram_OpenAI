"""Клиент для работы с OpenAI API через ProxyAPI."""
from openai import OpenAI
import logging
import asyncio
from typing import List, Dict, Optional
import config

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Клиент для взаимодействия с OpenAI API через ProxyAPI."""
    
    def __init__(self):
        """Инициализация клиента OpenAI с ProxyAPI."""
        self.client = OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.PROXYAPI_BASE_URL
        )
        self.model = config.OPENAI_MODEL
    
    def _get_response_sync(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """
        Синхронный метод для получения ответа от OpenAI API.
        
        Args:
            messages: Список сообщений для отправки в API
            
        Returns:
            Текст ответа от модели или None в случае ошибки
        """
        try:
            logger.info(f"Отправка запроса к OpenAI API. Модель: {self.model}, сообщений: {len(messages)}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Получен ответ от OpenAI API. Длина: {len(answer)} символов")
            
            return answer
            
        except Exception as e:
            logger.error(f"Ошибка при запросе к OpenAI API: {e}", exc_info=True)
            return None
    
    async def get_response(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """
        Асинхронный метод для получения ответа от OpenAI API.
        
        Args:
            messages: Список сообщений для отправки в API
            
        Returns:
            Текст ответа от модели или None в случае ошибки
        """
        # Выполняем синхронный вызов в отдельном потоке
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_response_sync, messages)
