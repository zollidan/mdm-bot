# MDM Bot - Docker Development

Этот файл содержит инструкции по запуску проекта через Docker.

## Быстрый старт

1. Убедитесь, что у вас установлен Docker и Docker Compose
2. Создайте `.env` файл с вашим токеном бота:

```env
BOT_TOKEN=your_bot_token_here
WEBAPP_URL=http://localhost:5173
```

3. Запустите все сервисы:

```bash
docker-compose up -d
```

## Сервисы

- **Backend**: http://localhost:8000
  - API документация: http://localhost:8000/docs
- **Frontend**: http://localhost:5173
- **Bot**: Telegram бот (фоновый процесс)

## Команды

### Запуск

```bash
docker-compose up -d
```

### Остановка

```bash
docker-compose down
```

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f bot
```

### Пересборка

```bash
docker-compose up -d --build
```

### Перезапуск сервиса

```bash
docker-compose restart backend
docker-compose restart bot
```

## Разработка

Для разработки рекомендуется запускать сервисы локально:

### Backend

```bash
uv run uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
bun run dev
```

### Bot

```bash
uv run python bot.py
```

## Production deployment

Для production необходимо:

1. Изменить `WEBAPP_URL` на публичный URL фронтенда
2. Настроить SSL сертификаты для HTTPS
3. Использовать внешнюю базу данных (PostgreSQL) вместо SQLite
4. Настроить reverse proxy (nginx) для API
5. Добавить мониторинг и логирование
