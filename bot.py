"""Основной файл Telegram-бота с интеграцией OpenAI через ProxyAPI."""
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

import config
from context_manager import ContextManager
from api_client import OpenAIClient

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Инициализация менеджеров
context_manager = ContextManager(max_messages=config.MAX_CONTEXT_MESSAGES)
openai_client = OpenAIClient()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start."""
    await message.answer(
        "Привет! Я бот с искусственным интеллектом.\n\n"
        "Я могу отвечать на ваши вопросы и помнить контекст диалога.\n"
        "Чтобы очистить контекст, напишите 'очистить контекст'.\n\n"
        "Задайте мне любой вопрос!"
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help."""
    await message.answer(
        "<b>Команды бота:</b>\n\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        "/clear - Очистить контекст диалога\n\n"
        "Просто напишите мне любое сообщение, и я отвечу!\n"
        "Я помню контекст диалога, так что можете задавать уточняющие вопросы."
    )


@dp.message(Command("clear", "reset"))
async def cmd_clear(message: Message):
    """Обработчик команд /clear и /reset для очистки контекста."""
    user_id = message.from_user.id
    context_manager.clear_context(user_id)
    await message.answer("Контекст диалога очищен. Начнем с чистого листа!")


@dp.message()
async def handle_message(message: Message):
    """Обработчик всех текстовых сообщений."""
    user_id = message.from_user.id
    user_text = message.text
    
    # Проверка на команду очистки контекста (без использования команды)
    if user_text.lower().strip() in ["очистить контекст", "очистить", "clear"]:
        context_manager.clear_context(user_id)
        await message.answer("Контекст диалога очищен. Начнем с чистого листа!")
        return
    
    # Показываем индикатор печати
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    # Получаем текущий контекст пользователя
    context = context_manager.get_context(user_id)
    
    # Добавляем сообщение пользователя в контекст
    context_manager.add_message(user_id, "user", user_text)
    
    # Обновляем контекст для запроса
    messages = context_manager.get_context(user_id)
    
    # Отправляем запрос к OpenAI API
    try:
        response_text = await openai_client.get_response(messages)
        
        if response_text:
            # Добавляем ответ ассистента в контекст
            context_manager.add_message(user_id, "assistant", response_text)
            
            # Отправляем ответ пользователю
            await message.answer(response_text)
            
            # Логируем статистику
            context_length = context_manager.get_context_length(user_id)
            logger.info(f"Пользователь {user_id}: отправлен ответ. Контекст: {context_length} сообщений")
        else:
            await message.answer(
                "Извините, произошла ошибка при обработке вашего запроса. "
                "Попробуйте еще раз позже."
            )
            logger.error(f"Ошибка: не удалось получить ответ от OpenAI для пользователя {user_id}")
    
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения от пользователя {user_id}: {e}", exc_info=True)
        await message.answer(
            "Произошла непредвиденная ошибка. Пожалуйста, попробуйте еще раз."
        )


async def main():
    """Основная функция запуска бота."""
    logger.info("Запуск бота...")
    
    try:
        # Проверка подключения к боту
        me = await bot.get_me()
        logger.info(f"Бот успешно запущен: @{me.username} ({me.first_name})")
        
        # Запуск polling
        await dp.start_polling(bot)
    
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске бота: {e}", exc_info=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
