# MDM Bot

Telegram бот с веб-приложением для управления каталогом товаров.

## Быстрый старт с Docker

```bash
# Создайте .env файл с токеном бота
cp .env.example .env
# Отредактируйте .env и добавьте свой BOT_TOKEN

# Запустите все сервисы
docker-compose up -d
```

Подробнее в [DOCKER.md](DOCKER.md)

## Установка для разработки

```bash
uv sync
```

## Настройка

1. Создайте Telegram бота через [@BotFather](https://t.me/botfather)
2. Скопируйте `.env.example` в `.env`
3. Добавьте токен бота в `.env`:

```env
BOT_TOKEN=your_bot_token_here
WEBAPP_URL=http://localhost:5173
```

## Запуск

### Backend (FastAPI)

```bash
uv run uvicorn main:app --reload
```

### Frontend (React)

```bash
cd frontend
bun run dev
```

### Telegram Bot

```bash
uv run python bot.py
```

## Структура проекта

- `main.py` - FastAPI backend
- `bot.py` - Telegram бот
- `models.py` - SQLAlchemy модели
- `schemas.py` - Pydantic схемы
- `crud.py` - CRUD операции
- `database.py` - Настройка БД
- `frontend/` - React приложение

## API

Документация API доступна на http://localhost:8000/docs
