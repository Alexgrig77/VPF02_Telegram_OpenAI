"""Конфигурация бота и загрузка переменных окружения."""
import os
from dotenv import load_dotenv

# Загрузка переменных из .env файла
load_dotenv()

# Токен Telegram бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле")

# API ключ OpenAI (ProxyAPI)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY не найден в .env файле")

# URL ProxyAPI
PROXYAPI_BASE_URL = "https://api.proxyapi.ru/openai/v1"

# Модель OpenAI
OPENAI_MODEL = "o4-mini-2025-04-16"

# Настройки для управления контекстом
MAX_CONTEXT_MESSAGES = 20  # Максимальное количество сообщений в контексте

# Параметры модели OpenAI (можно настраивать)
TEMPERATURE = 0.7  # Температура (0.0-2.0), влияет на креативность ответов
MAX_TOKENS = 1000  # Максимальное количество токенов в ответе (None для без ограничений)
