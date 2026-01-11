# Telegram бот с OpenAI через ProxyAPI

Telegram-бот на Python с использованием библиотеки aiogram и OpenAI API через ProxyAPI.

## Возможности

- Интеграция с OpenAI через ProxyAPI (модель o4-mini-2025-04-16)
- Запоминание контекста диалога для каждого пользователя
- Очистка контекста по команде
- Обработка ошибок и логирование

## Установка

1. Клонируйте репозиторий или скачайте файлы проекта

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` на основе `env_example.txt` и заполните токены:
```bash
BOT_TOKEN=ваш_токен_telegram_бота
OPENAI_API_KEY=ваш_ключ_proxyapi
```

   Для получения токенов:
   - **BOT_TOKEN**: Получите у [@BotFather](https://t.me/BotFather) в Telegram
   - **OPENAI_API_KEY**: Получите на [proxyapi.ru](https://proxyapi.ru)

## Запуск

```bash
python bot.py
```

## Команды бота

- `/start` - Начать работу с ботом
- `/help` - Показать справку
- `/clear` - Очистить контекст диалога

Также можно очистить контекст, написав "очистить контекст" в чате.

## Структура проекта

- `bot.py` - основной файл с логикой бота
- `config.py` - конфигурация и загрузка переменных окружения
- `context_manager.py` - управление контекстом диалогов
- `openai_client.py` - клиент для работы с ProxyAPI
- `.env` - файл с токенами (не загружается в Git)
- `requirements.txt` - зависимости проекта

## Используемые технологии

- Python 3.10+
- aiogram 3.0+
- openai (официальная библиотека)
- python-dotenv
- ProxyAPI для доступа к OpenAI API
