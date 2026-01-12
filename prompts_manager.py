"""Управление заготовленными промптами из JSON файла."""
import json
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class PromptsManager:
    """Менеджер для загрузки и работы с промптами из JSON файла."""
    
    def __init__(self, prompts_file: str = "prompts.json"):
        """
        Инициализация менеджера промптов.
        
        Args:
            prompts_file: Путь к JSON файлу с промптами
        """
        self.prompts_file = prompts_file
        self.prompts: Optional[List[Dict]] = None
        self._load_prompts()
    
    def _load_prompts(self) -> None:
        """Загружает промпты из JSON файла."""
        try:
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.prompts = data.get('prompts', [])
                logger.info(f"Загружено {len(self.prompts)} промптов из {self.prompts_file}")
        except FileNotFoundError:
            logger.warning(f"Файл {self.prompts_file} не найден. Промпты недоступны.")
            self.prompts = []
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка при парсинге JSON файла {self.prompts_file}: {e}")
            self.prompts = []
        except Exception as e:
            logger.error(f"Ошибка при загрузке промптов: {e}")
            self.prompts = []
    
    def get_prompts(self) -> List[Dict]:
        """
        Получить список всех промптов.
        
        Returns:
            Список промптов
        """
        return self.prompts or []
    
    def get_prompt_by_id(self, prompt_id: int) -> Optional[Dict]:
        """
        Получить промпт по ID.
        
        Args:
            prompt_id: ID промпта (1-based)
            
        Returns:
            Словарь с данными промпта или None
        """
        if not self.prompts:
            return None
        
        try:
            # Ищем промпт по id (1-based)
            for prompt in self.prompts:
                if prompt.get('id') == prompt_id:
                    return prompt
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении промпта по ID {prompt_id}: {e}")
            return None
    
    def format_prompts_list(self) -> str:
        """
        Форматирует список промптов для отображения пользователю.
        
        Returns:
            Отформатированная строка со списком промптов
        """
        if not self.prompts:
            return "❌ Промпты недоступны"
        
        lines = ["📋 <b>Доступные промпты:</b>\n"]
        for prompt in self.prompts:
            prompt_id = prompt.get('id', 0)
            name = prompt.get('name', 'Без названия')
            context = prompt.get('context', '')
            lines.append(f"<b>{prompt_id}.</b> {name}")
            if context:
                lines.append(f"   {context[:80]}{'...' if len(context) > 80 else ''}")
            lines.append("")
        
        return "\n".join(lines)
    
    def format_prompt_short(self) -> str:
        """
        Форматирует краткий список промптов (только ID и название).
        
        Returns:
            Отформатированная строка с кратким списком
        """
        if not self.prompts:
            return "❌ Промпты недоступны"
        
        lines = ["📋 <b>Выберите промпт:</b>\n"]
        for prompt in self.prompts:
            prompt_id = prompt.get('id', 0)
            name = prompt.get('name', 'Без названия')
            lines.append(f"<b>{prompt_id}.</b> {name}")
        
        return "\n".join(lines)
    
    def build_messages_with_prompt(self, prompt: Dict, user_input: str, 
                                   existing_context: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Формирует список сообщений для API с использованием промпта.
        
        Args:
            prompt: Словарь с данными промпта
            user_input: Текст пользователя
            existing_context: Существующий контекст диалога (опционально)
            
        Returns:
            Список сообщений для отправки в API
        """
        messages = []
        
        # Добавляем системное сообщение с ролью
        role = prompt.get('role', '')
        if role:
            messages.append({"role": "system", "content": role})
        
        # Добавляем существующий контекст (без системного сообщения, если оно уже есть)
        if existing_context:
            # Пропускаем системные сообщения из существующего контекста
            for msg in existing_context:
                if msg.get('role') != 'system':
                    messages.append(msg)
        
        # Формируем полный вопрос с контекстом
        question = prompt.get('question', '')
        format_text = prompt.get('format', '')
        
        full_question_parts = []
        if question:
            full_question_parts.append(question)
        if user_input:
            full_question_parts.append(f"\n\nТекст для обработки:\n{user_input}")
        if format_text:
            full_question_parts.append(f"\n\nФормат ответа: {format_text}")
        
        full_question = "".join(full_question_parts)
        messages.append({"role": "user", "content": full_question})
        
        return messages
