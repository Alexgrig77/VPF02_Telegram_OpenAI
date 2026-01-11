"""Управление контекстом диалогов пользователей."""
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class ContextManager:
    """Менеджер для хранения и управления контекстом диалогов пользователей."""
    
    def __init__(self, max_messages: int = 20):
        """
        Инициализация менеджера контекста.
        
        Args:
            max_messages: Максимальное количество сообщений в контексте пользователя
        """
        self.contexts: Dict[int, List[Dict[str, str]]] = {}
        self.max_messages = max_messages
    
    def get_context(self, user_id: int) -> List[Dict[str, str]]:
        """
        Получить контекст диалога пользователя.
        
        Args:
            user_id: ID пользователя Telegram
            
        Returns:
            Список сообщений в контексте пользователя
        """
        return self.contexts.get(user_id, [])
    
    def add_message(self, user_id: int, role: str, content: str) -> None:
        """
        Добавить сообщение в контекст пользователя.
        
        Args:
            user_id: ID пользователя Telegram
            role: Роль отправителя ('user' или 'assistant')
            content: Текст сообщения
        """
        if user_id not in self.contexts:
            self.contexts[user_id] = []
        
        self.contexts[user_id].append({"role": role, "content": content})
        
        # Ограничение размера контекста
        if len(self.contexts[user_id]) > self.max_messages:
            # Оставляем системное сообщение (если есть) и последние сообщения
            messages = self.contexts[user_id]
            # Если первое сообщение - системное, сохраняем его
            if messages and messages[0].get("role") == "system":
                self.contexts[user_id] = [messages[0]] + messages[-(self.max_messages - 1):]
            else:
                self.contexts[user_id] = messages[-self.max_messages:]
        
        logger.debug(f"Контекст пользователя {user_id}: {len(self.contexts[user_id])} сообщений")
    
    def clear_context(self, user_id: int) -> None:
        """
        Очистить контекст пользователя.
        
        Args:
            user_id: ID пользователя Telegram
        """
        if user_id in self.contexts:
            del self.contexts[user_id]
            logger.info(f"Контекст пользователя {user_id} очищен")
    
    def get_context_length(self, user_id: int) -> int:
        """
        Получить количество сообщений в контексте пользователя.
        
        Args:
            user_id: ID пользователя Telegram
            
        Returns:
            Количество сообщений в контексте
        """
        return len(self.contexts.get(user_id, []))
