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
            # Подготовка параметров запроса
            request_params = {
                "model": self.model,
                "messages": messages,
            }
            
            # Для модели o4-mini-2025-04-16 параметры temperature и max_tokens не поддерживаются
            # API использует значения по умолчанию для этой модели
            # Поэтому не передаем эти параметры
            
            logger.info(
                f"Отправка запроса к OpenAI API. "
                f"Модель: {self.model}, "
                f"Сообщений: {len(messages)}"
            )
            
            response = self.client.chat.completions.create(**request_params)
            
            # Логируем информацию об использованных токенах
            if hasattr(response, 'usage'):
                usage = response.usage
                prompt_tokens = getattr(usage, 'prompt_tokens', 0)
                completion_tokens = getattr(usage, 'completion_tokens', 0)
                total_tokens = getattr(usage, 'total_tokens', 0)
                
                logger.info(
                    f"Использовано токенов - Промпт: {prompt_tokens}, "
                    f"Ответ: {completion_tokens}, "
                    f"Всего: {total_tokens}"
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
