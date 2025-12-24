# Quick Start Guide

## Запуск проекта

### Вариант 1: Docker (Рекомендуется)

```bash
# 1. Создать .env файл
cp .env.example .env
# Отредактируйте .env и заполните переменные

# 2. Запустить все сервисы
docker compose up -d

# 3. Импортировать товары (если нужно)
docker compose exec bot uv run python -m mdm_bot.scripts.import_csv

# 4. Просмотреть логи
docker compose logs -f bot
docker compose logs -f api
```

### Вариант 2: Локальная разработка

```bash
# 1. Установить зависимости
uv sync --locked

# 2. Создать .env файл
cp .env.example .env
# Отредактируйте .env

# 3. Запустить PostgreSQL и MeiliSearch
docker compose up -d postgres meilisearch

# 4. Запустить бота
python -m mdm_bot.bot
# ИЛИ (старый способ)
python main.py

# 5. Запустить API (в другом терминале)
uvicorn mdm_bot.api.app:app --reload --host 0.0.0.0 --port 8000

# 6. Импортировать товары (если нужно)
python -m mdm_bot.scripts.import_csv
```

## Структура импортов

### Новый стиль (рекомендуется)

```python
# Основные модули
from mdm_bot.core import settings, AsyncSessionFactory, create_tables
from mdm_bot.core import User, Product, CartItem, Orders
from mdm_bot.core import MeiliSearchClient, get_meili_client

# Утилиты
from mdm_bot.utils import (
    get_main_keyboard,
    get_product_keyboard,
    format_product_card,
    format_main_page_text
)

# API
from mdm_bot.api import app
```

### Старый стиль (работает, но устарел)

```python
from config import settings
from database import AsyncSessionFactory
from models import User, Product
from kbs import main_kb, product_kb
from utils import make_product_card
```

## Полезные команды

```bash
# Просмотр логов
docker compose logs -f bot
docker compose logs -f api

# Перезапуск сервиса
docker compose restart bot
docker compose restart api

# Остановка всех сервисов
docker compose down

# Пересборка образа
docker compose build bot
docker compose up -d bot

# Подключение к контейнеру
docker compose exec bot bash

# Просмотр БД через postgresus
# Откройте http://localhost:4005
```

## Разработка

### Добавление нового хэндлера

1. Создайте файл в `mdm_bot/handlers/`:
```python
# mdm_bot/handlers/my_handler.py
from aiogram import Router
from aiogram.types import Message

router = Router()

@router.message()
async def my_handler(message: Message):
    await message.answer("Hello!")
```

2. Зарегистрируйте в `mdm_bot/handlers/__init__.py`:
```python
from .my_handler import router as my_router

__all__ = ["start_router", "my_router"]
```

3. Подключите в `mdm_bot/bot.py`:
```python
from mdm_bot.handlers import start_router, my_router

dp.include_router(start_router)
dp.include_router(my_router)
```

## Миграция на новую структуру

Если у вас есть старый код:

1. Замените импорты:
```python
# Было
from config import settings
from models import User

# Стало
from mdm_bot.core import settings, User
```

2. Замените вызовы функций в utils:
```python
# Было
from kbs import main_kb
keyboard = main_kb()

# Стало
from mdm_bot.utils import get_main_keyboard
keyboard = get_main_keyboard()
```

3. Обновите команды запуска:
```bash
# Было
python main.py

# Стало
python -m mdm_bot.bot
```

## Поддержка

- Документация: [README.md](README.md)
- Структура проекта: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- Инструкции для Claude: [CLAUDE.md](CLAUDE.md)
