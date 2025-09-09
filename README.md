MDM Bot

Описание
- Telegram-бот для поиска товаров, добавления в избранное и корзину, оформления заказов и просмотра профиля.

Требования
- Python 3.10+
- Токен бота Telegram в `.env` (`BOT_TOKEN=...`).

Установка
- Создать и активировать venv:
  - Windows PowerShell: `python -m venv .venv; .\\.venv\\Scripts\\Activate.ps1`
  - Unix: `python -m venv .venv && source .venv/bin/activate`
- Установить зависимости: `pip install -U pip && pip install -e .` или `pip install aiogram art asyncpg psycopg2 pydantic-settings "sqlalchemy[asyncio]"`

Настройка
- Скопировать `.env.example` в `.env` и указать `BOT_TOKEN`.
- По умолчанию используется SQLite `test.db`. Настройки PostgreSQL можно включить в `database.py` и `.env` при необходимости.

Загрузка товаров (seed)
- Положить CSV `old_db_lite.csv` в корень (разделитель `;`).
- Запустить: `python convert.py` — создаст таблицы и импортирует товары.

Запуск бота
- `python main.py`

Основные команды/функции
- `/start` — регистрация и главное меню.
- Поиск по артикулу и названию, карточка товара с картинкой, добавление/удаление из корзины и избранного.
- Корзина, оформление заказа, список заказов и детали.
- Профиль: просмотр/изменение имени, телефона, адреса.
- Помощь: контакты.

Примечания
- Для разработки используется SQLite; для продакшена переключитесь на Postgres.
- См. PLAN.md для плана работ до MVP.
