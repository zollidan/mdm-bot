# MDM Bot - Telegram E-commerce Bot

Telegram бот для каталога товаров с поиском через MeiliSearch, корзиной, избранным и оформлением заказов.

## 🚀 Быстрый старт

### 1. Настройка окружения

```bash
# Скопируйте шаблон .env
cp .env.example .env

# Отредактируйте .env и укажите:
# - BOT_TOKEN (от @BotFather)
# - POSTGRES_PASSWORD (надежный пароль)
# - MEILI_MASTER_KEY (минимум 16 символов)
# - WEBAPP_URL (ваш домен, например https://mdm-bot.duckdns.org)
nano .env
```

### 2. Запуск через Docker

```bash
# Запустить все сервисы
docker compose up -d

# Проверить статус
docker compose ps

# Посмотреть логи бота
docker compose logs -f bot
```

### 3. Импорт товаров (опционально)

```bash
# Положите old_db_lite.csv в корень проекта
docker compose exec bot uv run convert.py
```

## 📦 Что включено

**Сервисы:**
- **Bot** - Telegram бот на aiogram 3.x
- **PostgreSQL** - База данных (порт 5432)
- **MeiliSearch** - Поисковый движок (порт 7700)
- **Postgresus** - Админка PostgreSQL (порт 4005)
- **API** - FastAPI REST API (порт 8000)
- **WebApp** - Vue.js Mini App (порт 80)

## 🎯 Основные функции

✅ **Поиск** - Полнотекстовый поиск по названию и артикулу
✅ **Каталог** - Mini App с каталогом товаров
✅ **Корзина** - Добавление/удаление товаров, оформление заказа
✅ **Избранное** - Сохранение товаров для быстрого доступа
✅ **Заказы** - История заказов с деталями
✅ **Профиль** - Управление именем, телефоном, адресом доставки

## 🏗️ Архитектура

```
Telegram Bot (main.py)
    ↓
SQLAlchemy + PostgreSQL
    ↓
MeiliSearch (full-text search)

Vue.js Mini App
    ↓
FastAPI REST API
    ↓
PostgreSQL
```

**Структура файлов:**
```
├── main.py           # Bot handlers, FSM states
├── models.py         # SQLAlchemy models
├── database.py       # Database connection
├── config.py         # Settings (pydantic-settings)
├── kbs.py            # Keyboard builders
├── utils.py          # Text formatters
├── convert.py        # CSV import script
├── api_server.py     # FastAPI REST API
├── webapp/           # Vue.js Mini App
└── docker-compose.yaml
```

## 🔧 Полезные команды

```bash
# Перезапустить бота
docker compose restart bot

# Логи всех сервисов
docker compose logs -f

# Логи конкретного сервиса
docker compose logs -f bot
docker compose logs -f postgres

# Остановить все сервисы
docker compose down

# Обновить и пересобрать
docker compose up -d --build

# Бэкап базы данных
docker compose exec postgres pg_dump -U postgres mdm_db > backup.sql

# Проверить здоровье сервисов
curl http://localhost:8000/api/health
curl http://localhost:7700/health
```

## 🔐 Безопасность

- ✅ Используйте надежные пароли для `POSTGRES_PASSWORD`
- ✅ Генерируйте случайный `MEILI_MASTER_KEY` (минимум 16 символов)
- ✅ Не коммитьте `.env` файлы (уже в .gitignore)
- ✅ Для production используйте HTTPS для WEBAPP_URL
- ✅ Закройте внешний доступ к портам PostgreSQL и MeiliSearch

## 🌍 Production развертывание

### Требования
- Docker и Docker Compose
- Домен с SSL сертификатом (для Mini App)
- Открытые порты: 80 (webapp), 8000 (api)

### Настройка

1. **Получите SSL сертификат**
```bash
# Пример с Let's Encrypt
certbot certonly --standalone -d mdm-bot.duckdns.org
```

2. **Обновите .env**
```env
WEBAPP_URL=https://mdm-bot.duckdns.org
MEILI_ENV=production
```

3. **Запустите сервисы**
```bash
docker compose up -d
```

4. **Проверьте работу**
- Откройте бота в Telegram
- Отправьте `/start`
- Нажмите "🛍️ Открыть каталог"

## 💻 Локальная разработка

```bash
# Установите зависимости Python
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Запустите PostgreSQL и MeiliSearch
docker compose up -d postgres meilisearch

# Настройте .env для локальной разработки
POSTGRES_HOST=localhost
WEBAPP_URL=http://localhost

# Запустите бота
python main.py

# В другом терминале - API
python api_server.py

# В третьем терминале - Mini App
cd webapp
npm install
npm run dev
```

## 📊 Переменные окружения

| Переменная | Описание | Пример |
|-----------|----------|--------|
| `BOT_TOKEN` | Токен от @BotFather | `123456:ABC-DEF...` |
| `POSTGRES_USER` | Пользователь БД | `postgres` |
| `POSTGRES_PASSWORD` | Пароль БД | `SecurePassword123` |
| `POSTGRES_HOST` | Хост БД | `postgres` (Docker) / `localhost` |
| `POSTGRES_PORT` | Порт БД | `5432` |
| `POSTGRES_DB` | Имя БД | `mdm_db` |
| `MEILI_HOST` | Хост MeiliSearch | `meilisearch` |
| `MEILI_PORT` | Порт MeiliSearch | `7700` |
| `MEILI_MASTER_KEY` | Мастер-ключ | Минимум 16 символов |
| `MEILI_ENV` | Режим | `development` / `production` |
| `WEBAPP_URL` | URL Mini App | `https://your-domain.com` |

## 🐛 Troubleshooting

**Бот не запускается?**
```bash
docker compose logs bot
# Проверьте BOT_TOKEN в .env
```

**Ошибка подключения к БД?**
```bash
docker compose ps postgres
docker compose logs postgres
# Проверьте POSTGRES_* переменные
```

**MeiliSearch не работает?**
```bash
curl http://localhost:7700/health
docker compose logs meilisearch
# Проверьте MEILI_MASTER_KEY (минимум 16 символов)
```

**Mini App не открывается?**
```bash
# Проверьте WEBAPP_URL в .env
# Для production требуется HTTPS
docker compose logs webapp
docker compose logs api
```

## 📚 Структура базы данных

**Таблицы:**
- `users` - Пользователи Telegram
- `products` - Товары каталога
- `cart_items` - Корзина покупок
- `favorites` - Избранные товары
- `orders` - Заказы
- `order_items` - Позиции в заказах
- `reviews` - Отзывы (placeholder)

## 🎨 Кастомизация

**Изменить текст приветствия:**
Отредактируйте `welcome_message` в [main.py:74](main.py#L74)

**Добавить новую кнопку в меню:**
Отредактируйте функцию `main_kb()` в [kbs.py:11](kbs.py#L11)

**Изменить количество товаров в поиске:**
Измените параметр `limit` в [main.py:192](main.py#L192)

## 📝 Лицензия

MIT

## 🆘 Поддержка

При возникновении проблем:
1. Проверьте логи: `docker compose logs -f`
2. Проверьте переменные окружения в `.env`
3. Проверьте статус сервисов: `docker compose ps`
4. Создайте issue в репозитории
