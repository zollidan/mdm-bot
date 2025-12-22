# MDM Bot Telegram Mini App

Веб-приложение для каталога товаров MDM Bot, построенное на Vue.js 3 и Vite.

## Структура проекта

```
webapp/
├── src/
│   ├── components/       # Vue компоненты
│   │   └── ProductList.vue
│   ├── api/             # API клиенты
│   │   └── products.js
│   ├── App.vue          # Главный компонент
│   ├── main.js          # Точка входа
│   └── style.css        # Глобальные стили
├── public/              # Статические файлы
├── index.html           # HTML шаблон
├── vite.config.js       # Конфигурация Vite
├── package.json         # Зависимости
├── Dockerfile           # Docker образ для production
└── nginx.conf           # Nginx конфигурация
```

## Разработка

### Локальный запуск

1. Установите зависимости:
```bash
cd webapp
npm install
```

2. Запустите dev сервер:
```bash
npm run dev
```

Приложение будет доступно по адресу `http://localhost:5173`

### Сборка для production

```bash
npm run build
```

Собранные файлы будут в папке `dist/`

## Docker

### Сборка образа

```bash
docker build -t mdm-webapp .
```

### Запуск контейнера

```bash
docker run -p 80:80 mdm-webapp
```

## Интеграция с Telegram

Приложение использует Telegram Web App API для:
- Получения темы оформления Telegram
- Отправки данных обратно в бот при клике на товар
- Адаптации интерфейса под Telegram

### Переменные окружения

Создайте `.env` файл в папке `webapp/`:

```env
VITE_API_URL=http://localhost:8000/api
```

## Функционал

- ✅ Список товаров с изображениями
- ✅ Пагинация (20 товаров на страницу)
- ✅ Адаптивный дизайн
- ✅ Интеграция с Telegram темой
- ✅ Отправка событий в бот при клике на товар

## API Endpoints

Приложение использует следующие API эндпоинты:

- `GET /api/products?page=1&limit=20` - Получить список товаров
- `GET /api/products/{id}` - Получить информацию о товаре

## Технологии

- Vue.js 3 - JavaScript фреймворк
- Vite - Сборщик и dev сервер
- Telegram Web App API - Интеграция с Telegram
- Axios - HTTP клиент
- Nginx - Web сервер для production
