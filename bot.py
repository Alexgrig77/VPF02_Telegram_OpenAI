"""Основной файл Telegram-бота с интеграцией OpenAI через ProxyAPI."""
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

import config
from context_manager import ContextManager
from api_client import OpenAIClient
from prompts_manager import PromptsManager

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
dp = Dispatcher(storage=MemoryStorage())

# Инициализация менеджеров
context_manager = ContextManager(max_messages=config.MAX_CONTEXT_MESSAGES)
openai_client = OpenAIClient()
prompts_manager = PromptsManager()

# Хранение выбранных промптов для пользователей
user_selected_prompts = {}


class PromptStates(StatesGroup):
    """Состояния для выбора промпта."""
    waiting_for_prompt_choice = State()


@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start."""
    user_id = message.from_user.id
    # Очищаем контекст и выбранный промпт
    context_manager.clear_context(user_id)
    if user_id in user_selected_prompts:
        del user_selected_prompts[user_id]
    await state.clear()
    
    # Проверяем наличие промптов и предлагаем их использовать
    prompts = prompts_manager.get_prompts()
    if prompts:
        await message.answer(
            "Привет! Я бот с искусственным интеллектом.\n\n"
            "Я могу отвечать на ваши вопросы и помнить контекст диалога.\n"
            "Чтобы очистить контекст, напишите 'очистить контекст'.\n\n"
            "🤔 Хотите использовать специальный промпт для ответа?\n\n"
            "Специальные промпты помогают получить более структурированные и "
            "профессиональные ответы для конкретных задач.\n\n"
            "Введите <b>да</b> для выбора промпта или <b>нет</b> для обычного режима."
        )
    else:
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
async def cmd_clear(message: Message, state: FSMContext):
    """Обработчик команд /clear и /reset для очистки контекста."""
    user_id = message.from_user.id
    context_manager.clear_context(user_id)
    if user_id in user_selected_prompts:
        del user_selected_prompts[user_id]
    await state.clear()
    await message.answer("Контекст диалога очищен. Начнем с чистого листа!")


@dp.message(PromptStates.waiting_for_prompt_choice)
async def handle_prompt_choice(message: Message, state: FSMContext):
    """Обработчик выбора промпта по номеру."""
    user_id = message.from_user.id
    user_text = message.text.strip()
    
    # Проверка на отмену
    if user_text.lower() in ["отмена", "cancel", "нет", "no", "0"]:
        await state.clear()
        if user_id in user_selected_prompts:
            del user_selected_prompts[user_id]
        await message.answer("Выбор промпта отменен. Работаю в обычном режиме.")
        return
    
    # Пытаемся распарсить номер промпта
    try:
        prompt_id = int(user_text)
        prompt = prompts_manager.get_prompt_by_id(prompt_id)
        
        if prompt:
            user_selected_prompts[user_id] = prompt
            await state.clear()
            await message.answer(
                f"✅ Выбран промпт: <b>{prompt['name']}</b>\n\n"
                f"Роль: {prompt.get('role', '')}\n"
                f"Контекст: {prompt.get('context', '')}\n\n"
                f"Теперь задайте ваш вопрос, и я отвечу с использованием этого промпта."
            )
        else:
            await message.answer(
                f"❌ Промпт с номером {prompt_id} не найден.\n"
                f"Пожалуйста, введите номер от 1 до {len(prompts_manager.get_prompts())} или 'отмена'."
            )
    except ValueError:
        await message.answer(
            "❌ Пожалуйста, введите номер промпта (цифру) или 'отмена' для отмены."
        )


@dp.message()
async def handle_message(message: Message, state: FSMContext):
    """Обработчик всех текстовых сообщений."""
    user_id = message.from_user.id
    user_text = message.text
    
    # Проверка на команду очистки контекста (без использования команды)
    if user_text.lower().strip() in ["очистить контекст", "очистить", "clear"]:
        context_manager.clear_context(user_id)
        if user_id in user_selected_prompts:
            del user_selected_prompts[user_id]
        await state.clear()
        await message.answer("Контекст диалога очищен. Начнем с чистого листа!")
        return
    
    # Проверяем, есть ли у пользователя выбранный промпт
    selected_prompt = user_selected_prompts.get(user_id)
    
    # Если промпт не выбран и это первое сообщение в контексте, предлагаем использовать промпты
    if not selected_prompt and context_manager.get_context_length(user_id) == 0:
        prompts = prompts_manager.get_prompts()
        if prompts:
            # Проверяем, является ли сообщение ответом на предложение использовать промпты
            user_text_lower = user_text.lower().strip()
            
            if user_text_lower in ["да", "yes", "y", "использовать", "use"]:
                # Пользователь хочет использовать промпты
                prompts_list = prompts_manager.format_prompt_short()
                await message.answer(
                    f"{prompts_list}\n\n"
                    "Введите <b>номер</b> промпта для выбора или <b>отмена</b> для обычного режима."
                )
                await state.set_state(PromptStates.waiting_for_prompt_choice)
                return
            elif user_text_lower in ["нет", "no", "n", "не использовать"]:
                # Пользователь не хочет использовать промпты - продолжаем как обычный запрос
                await message.answer("Хорошо, работаю в обычном режиме. Обрабатываю ваш вопрос...")
                # Продолжаем обработку как обычный запрос (не делаем return)
            else:
                # Пользователь написал что-то другое - предлагаем использовать промпты
                await message.answer(
                    "🤔 Хотите использовать специальный промпт для ответа?\n\n"
                    "Специальные промпты помогают получить более структурированные и "
                    "профессиональные ответы для конкретных задач.\n\n"
                    "Введите <b>да</b> для выбора промпта или <b>нет</b> для обычного режима.\n\n"
                    "Или просто задайте ваш вопрос, и я обработаю его в обычном режиме."
                )
                return
    
    # Если мы в состоянии ожидания выбора промпта, но получили обычное сообщение
    current_state = await state.get_state()
    if current_state == PromptStates.waiting_for_prompt_choice:
        # Перенаправляем в обработчик выбора промпта
        await handle_prompt_choice(message, state)
        return
    
    # Показываем индикатор печати
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    # Получаем текущий контекст пользователя
    existing_context = context_manager.get_context(user_id)
    
    # Формируем сообщения для API
    if selected_prompt:
        # Используем промпт для формирования запроса
        messages = prompts_manager.build_messages_with_prompt(
            selected_prompt, 
            user_text, 
            existing_context
        )
        # Добавляем сообщение пользователя в контекст (для истории)
        context_manager.add_message(user_id, "user", user_text)
    else:
        # Обычный режим без промпта
        context_manager.add_message(user_id, "user", user_text)
        messages = context_manager.get_context(user_id)
    
    # Отправляем запрос к OpenAI API
    try:
        response_text = await openai_client.get_response(messages)
        
        if response_text:
            # Добавляем ответ ассистента в контекст
            context_manager.add_message(user_id, "assistant", response_text)
            
            # Отправляем ответ пользователю без HTML-парсинга, чтобы избежать ошибок парсинга
            # Если ответ слишком длинный, разбиваем на части
            max_length = 4096  # Максимальная длина сообщения в Telegram
            if len(response_text) > max_length:
                # Разбиваем на части
                parts = []
                current_part = ""
                for line in response_text.split('\n'):
                    if len(current_part) + len(line) + 1 > max_length:
                        if current_part:
                            parts.append(current_part)
                        current_part = line
                    else:
                        current_part += '\n' + line if current_part else line
                if current_part:
                    parts.append(current_part)
                
                for part in parts:
                    await message.answer(part, parse_mode=None)
            else:
                await message.answer(response_text, parse_mode=None)
            
            # Логируем статистику
            context_length = context_manager.get_context_length(user_id)
            prompt_name = selected_prompt['name'] if selected_prompt else "обычный режим"
            logger.info(
                f"Пользователь {user_id}: отправлен ответ. "
                f"Контекст: {context_length} сообщений. "
                f"Промпт: {prompt_name}"
            )
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
