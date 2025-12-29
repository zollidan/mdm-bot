# План миграции MDM Bot с Python на Golang

## 📊 Анализ текущего проекта

**Текущий стек (Python):**
- **Bot**: aiogram 3.x (~400 строк в bot.py + handlers)
- **API**: FastAPI (~237 строк в api/app.py)
- **Database**: SQLAlchemy async + PostgreSQL (139 строк models)
- **Search**: MeiliSearch client
- **Config**: pydantic-settings
- **Всего**: ~1200 строк Python кода

**Структура проекта:**
```
mdm_bot/
├── core/
│   ├── config.py         # Конфигурация через pydantic-settings
│   ├── models.py         # 6 моделей: User, Product, CartItem, Favorite, Orders, OrderItems
│   ├── database.py       # Async SQLAlchemy engine + session factory
│   └── search.py         # MeiliSearch integration
├── handlers/
│   └── start.py          # /start handler
├── utils/
│   ├── keyboards.py      # 10+ keyboard builders для UI
│   └── formatters.py     # Text formatting utilities
├── api/
│   └── app.py            # FastAPI REST endpoints (3 routes)
├── scripts/
│   └── import_csv.py     # CSV import script
└── bot.py                # Main bot entry point
```

---

## 🎯 Целевая архитектура (Golang)

### Структура проекта Go

```
mdm-bot-go/
├── cmd/
│   ├── bot/              # Telegram bot executable
│   │   └── main.go
│   ├── api/              # REST API executable
│   │   └── main.go
│   └── importer/         # CSV importer tool
│       └── main.go
├── internal/
│   ├── config/           # Конфигурация (viper + godotenv)
│   │   └── config.go
│   ├── models/           # Database models (GORM)
│   │   ├── user.go
│   │   ├── product.go
│   │   ├── cart.go
│   │   ├── favorite.go
│   │   └── order.go
│   ├── database/         # DB connection & migrations
│   │   └── db.go
│   ├── search/           # MeiliSearch client
│   │   └── meili.go
│   ├── bot/              # Bot logic
│   │   ├── handlers/     # Message & callback handlers
│   │   ├── keyboards/    # Inline keyboard builders
│   │   └── formatters/   # Text utilities
│   ├── api/              # REST API handlers
│   │   └── handlers.go
│   └── repository/       # Data access layer (опционально)
│       ├── user.go
│       ├── product.go
│       └── order.go
├── pkg/                  # Публичные библиотеки (если нужны)
├── migrations/           # SQL migrations (goose/migrate)
├── .env.example
├── go.mod
├── go.sum
├── Dockerfile.bot
├── Dockerfile.api
├── docker-compose.yml
└── README.md
```

---

## 📚 Библиотеки Golang

### 1. Telegram Bot Framework
**Выбор: `gopkg.in/telebot.v3`**
- Наиболее похож на aiogram по API
- Поддержка FSM через middleware
- Удобные builder'ы для клавиатур

```go
// Установка
go get gopkg.in/telebot.v3

// Пример использования
bot.Handle("/start", func(c telebot.Context) error {
    return c.Send("Привет!")
})
```

**Альтернатива**: `github.com/go-telegram-bot-api/telegram-bot-api/v5` (более низкоуровневая)

### 2. Database ORM
**Выбор: `gorm.io/gorm`**
- Самая популярная ORM для Go
- Автомиграции схемы
- Preload для связей (как в SQLAlchemy)

```go
// Установка
go get gorm.io/gorm
go get gorm.io/driver/postgres

// Пример модели
type User struct {
    gorm.Model
    TelegramID  int64  `gorm:"primaryKey"`
    Username    string
    PhoneNumber string
    Address     string
}
```

### 3. REST API Framework
**Выбор: `github.com/gofiber/fiber/v2`**
- Самый быстрый Go framework (10x быстрее FastAPI)
- Синтаксис похож на Express.js
- Встроенная валидация и middleware

```go
// Установка
go get github.com/gofiber/fiber/v2

// Пример endpoint
app.Get("/api/products", func(c *fiber.Ctx) error {
    return c.JSON(products)
})
```

**Альтернатива**: `github.com/gin-gonic/gin` (более популярная, но медленнее)

### 4. Конфигурация
**Выбор: `github.com/spf13/viper` + `github.com/joho/godotenv`**

```go
// Установка
go get github.com/spf13/viper
go get github.com/joho/godotenv

// Загрузка .env
viper.SetConfigFile(".env")
viper.AutomaticEnv()
botToken := viper.GetString("BOT_TOKEN")
```

### 5. MeiliSearch Client
**Официальный клиент: `github.com/meilisearch/meilisearch-go`**

```go
go get github.com/meilisearch/meilisearch-go
```

### 6. Дополнительные утилиты
- `github.com/golang-migrate/migrate` - миграции БД
- `github.com/rs/zerolog` - структурированный logging
- `github.com/stretchr/testify` - тестирование

---

## 🗓️ Поэтапный план миграции

### **Фаза 1: Подготовка и инфраструктура (2-3 дня)**

#### День 1: Инициализация проекта
- [ ] Создать новую директорию `mdm-bot-go/`
- [ ] Инициализировать Go модуль: `go mod init github.com/username/mdm-bot-go`
- [ ] Настроить структуру директорий (cmd/, internal/)
- [ ] Скопировать и адаптировать `.env.example`
- [ ] Настроить `.gitignore` для Go

#### День 2: База данных и модели
- [ ] Установить GORM и PostgreSQL драйвер
- [ ] Создать `internal/config/config.go` (миграция config.py)
- [ ] Создать `internal/database/db.go` (подключение к БД)
- [ ] Мигрировать модели из `models.py` в Go:
  - [ ] `internal/models/user.go` → User model
  - [ ] `internal/models/product.go` → Product model
  - [ ] `internal/models/cart.go` → CartItem model
  - [ ] `internal/models/favorite.go` → Favorite model
  - [ ] `internal/models/order.go` → Orders + OrderItems models
- [ ] Настроить автомиграции GORM
- [ ] Написать тесты для моделей

#### День 3: MeiliSearch интеграция
- [ ] Создать `internal/search/meili.go`
- [ ] Реализовать методы:
  - [ ] `InitClient()` - подключение к MeiliSearch
  - [ ] `SyncProducts()` - индексация продуктов
  - [ ] `SearchProducts(query string, limit int)` - поиск
- [ ] Протестировать поиск

---

### **Фаза 2: REST API (2-3 дня)**

#### День 4: Базовый API
- [ ] Создать `cmd/api/main.go`
- [ ] Настроить Fiber app с CORS middleware
- [ ] Реализовать endpoints из `api/app.py`:
  - [ ] `GET /api/products` - список товаров с пагинацией
  - [ ] `GET /api/products/:id` - детали товара
  - [ ] `GET /api/search` - поиск товаров
  - [ ] `GET /api/health` - health check
- [ ] Создать Pydantic-подобные structs для валидации:
  ```go
  type ProductResponse struct {
      ID          int     `json:"id"`
      Name        string  `json:"name"`
      Price       float64 `json:"price"`
      Image       string  `json:"image,omitempty"`
      VendorCode  string  `json:"vendor_code,omitempty"`
      Description string  `json:"description,omitempty"`
  }
  ```

#### День 5: HTML templates и статика
- [ ] Настроить Fiber template engine (html/template)
- [ ] Мигрировать HTML routes:
  - [ ] `GET /` - главная страница
  - [ ] `GET /products` - каталог
  - [ ] `GET /products/:id` - детали товара
  - [ ] `GET /support` - поддержка
- [ ] Настроить статический файл сервер `app.Static("/static", "./static")`

#### День 6: Тестирование API
- [ ] Написать integration tests для API endpoints
- [ ] Проверить CORS настройки
- [ ] Создать Dockerfile для API
- [ ] Протестировать с фронтендом (Vue.js Mini App)

---

### **Фаза 3: Telegram Bot (5-7 дней)**

#### День 7-8: Базовая инициализация бота
- [ ] Создать `cmd/bot/main.go`
- [ ] Настроить telebot.v3:
  ```go
  bot, err := telebot.NewBot(telebot.Settings{
      Token:  config.BotToken,
      Poller: &telebot.LongPoller{Timeout: 10 * time.Second},
  })
  ```
- [ ] Реализовать `/start` handler (из `handlers/start.py`):
  - [ ] Создание/обновление пользователя в БД
  - [ ] Отправка welcome message
  - [ ] Web App button для каталога
- [ ] Создать `internal/bot/keyboards/main.go` - главное меню
- [ ] Протестировать базовую работу бота

#### День 9: Клавиатуры и навигация
Мигрировать все клавиатуры из `utils/keyboards.py`:
- [ ] `GetMainKeyboard()` - главное меню (8 кнопок)
- [ ] `GetProductKeyboard()` - карточка товара (корзина/избранное)
- [ ] `GetCartKeyboard()` - корзина с товарами
- [ ] `GetFavoritesKeyboard()` - избранное
- [ ] `GetOrdersKeyboard()` - список заказов
- [ ] `GetProfileKeyboard()` - профиль пользователя
- [ ] `GetHelpKeyboard()` - помощь

#### День 10: Callback handlers (часть 1)
Реализовать базовые callback handlers:
- [ ] `callback_data == "main_page"` - главное меню
- [ ] `callback_data == "help"` - помощь
- [ ] `callback_data == "profile"` - профиль пользователя
- [ ] `callback_data == "cart"` - корзина
- [ ] `callback_data == "favorites"` - избранное
- [ ] `callback_data == "orders"` - заказы

#### День 11: Работа с товарами
- [ ] `view_product_{id}` - просмотр товара
- [ ] `add_cart_{id}` - добавить в корзину
- [ ] `remove_cart_{id}` - удалить из корзины
- [ ] `add_fav_{id}` - добавить в избранное
- [ ] `remove_fav_{id}` - удалить из избранного
- [ ] Создать `internal/bot/formatters/product.go` для форматирования карточек товара

#### День 12: FSM (Finite State Machine)
Реализовать состояния для multi-step flows:
- [ ] Поиск товаров:
  - [ ] Состояние `SearchForm` - ожидание текста запроса
  - [ ] Поиск через MeiliSearch
  - [ ] Отображение результатов (макс 5)
- [ ] Редактирование профиля:
  - [ ] `ProfileForm.name` - изменение имени
  - [ ] `ProfileForm.phone` - изменение телефона (валидация regex)
  - [ ] `ProfileForm.address` - изменение адреса

**Примечание**: FSM в telebot реализуется через middleware или context storage

#### День 13: Обработка заказов
- [ ] `checkout` callback - оформление заказа
  - [ ] Проверка заполненности профиля (имя, телефон, адрес)
  - [ ] Создание заказа в БД
  - [ ] Перенос товаров из корзины в OrderItems
  - [ ] Очистка корзины
  - [ ] Отправка подтверждения пользователю
- [ ] `order_details_{id}` - детали заказа
- [ ] Форматирование списка заказов по датам

#### День 14: Финальные фичи и polish
- [ ] Обработка ошибок (graceful error messages)
- [ ] Логирование (zerolog)
- [ ] Middleware для метрик (опционально)
- [ ] Рефакторинг повторяющегося кода

---

### **Фаза 4: Утилиты и скрипты (1 день)**

#### День 15: CSV Importer
- [ ] Создать `cmd/importer/main.go`
- [ ] Мигрировать логику из `scripts/import_csv.py`:
  - [ ] Парсинг CSV (semicolon delimiter)
  - [ ] Маппинг колонок в Product модель
  - [ ] Bulk insert в PostgreSQL
  - [ ] Индексация в MeiliSearch
- [ ] Тестирование импорта

---

### **Фаза 5: Docker и деплой (2 дня)**

#### День 16: Dockerization
- [ ] Создать `Dockerfile.bot` (multi-stage build):
  ```dockerfile
  # Stage 1: Build
  FROM golang:1.21-alpine AS builder
  WORKDIR /app
  COPY go.mod go.sum ./
  RUN go mod download
  COPY . .
  RUN CGO_ENABLED=0 GOOS=linux go build -o bot cmd/bot/main.go

  # Stage 2: Run
  FROM alpine:latest
  WORKDIR /root/
  COPY --from=builder /app/bot .
  CMD ["./bot"]
  ```
- [ ] Создать `Dockerfile.api` (аналогично)
- [ ] Обновить `docker-compose.yml`:
  - Заменить Python сервисы на Go
  - Оставить PostgreSQL, MeiliSearch без изменений
  - Добавить health checks

#### День 17: Тестирование и оптимизация
- [ ] Запустить полный стек через `docker compose up`
- [ ] Протестировать все функции бота
- [ ] Протестировать API с Mini App
- [ ] Сравнить потребление ресурсов:
  - Python bot: ~200-400MB RAM
  - Go bot: ~50-100MB RAM (ожидаемо)
- [ ] Проверить logs и мониторинг
- [ ] Финальные исправления

---

## 📋 Чеклист миграции

### Модели данных
- [ ] User
- [ ] Product (24 поля + складские остатки)
- [ ] CartItem
- [ ] Favorite
- [ ] Orders
- [ ] OrderItems
- [ ] Reviews (placeholder)

### API Endpoints
- [ ] GET /api/products (pagination)
- [ ] GET /api/products/:id
- [ ] GET /api/search
- [ ] GET /api/health
- [ ] GET / (HTML)
- [ ] GET /products (HTML)
- [ ] GET /products/:id (HTML)
- [ ] GET /support (HTML)

### Bot Commands
- [ ] /start

### Bot Callbacks
- [ ] main_page
- [ ] search (FSM)
- [ ] cart
- [ ] favorites
- [ ] orders
- [ ] profile
- [ ] help
- [ ] view_product_{id}
- [ ] add_cart_{id}
- [ ] remove_cart_{id}
- [ ] add_fav_{id}
- [ ] remove_fav_{id}
- [ ] checkout
- [ ] order_details_{id}
- [ ] edit_name (FSM)
- [ ] edit_phone (FSM)
- [ ] edit_address (FSM)

### Keyboards (10 builders)
- [ ] Main keyboard
- [ ] Product keyboard
- [ ] Cart keyboard
- [ ] Favorites keyboard
- [ ] Orders keyboard
- [ ] Profile keyboard
- [ ] Help keyboard
- [ ] Empty cart keyboard
- [ ] Product not found keyboard

### Утилиты
- [ ] CSV importer
- [ ] Text formatters
- [ ] Product card builder

---

## 🔄 Сравнение кода: Python vs Go

### Пример 1: Модель User

**Python (SQLAlchemy):**
```python
class User(Base):
    __tablename__ = 'users'

    telegram_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(), nullable=True)
    name: Mapped[str] = mapped_column(String())
    phone_number: Mapped[str] = mapped_column(String())
    address: Mapped[str] = mapped_column(String())

    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user")
    orders: Mapped[list["Orders"]] = relationship(back_populates="user")
```

**Golang (GORM):**
```go
type User struct {
    TelegramID  int64  `gorm:"primaryKey" json:"telegram_id"`
    Username    string `json:"username"`
    Name        string `json:"name"`
    PhoneNumber string `json:"phone_number"`
    Address     string `json:"address"`
    CreatedAt   time.Time

    Favorites []Favorite `gorm:"foreignKey:UserID" json:"favorites,omitempty"`
    Orders    []Order    `gorm:"foreignKey:UserID" json:"orders,omitempty"`
}
```

### Пример 2: API Endpoint

**Python (FastAPI):**
```python
@app.get("/api/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    async with AsyncSessionFactory() as session:
        query = select(Product).where(Product.id == product_id)
        result = await session.execute(query)
        product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(status_code=404, detail="Товар не найден")

        return ProductResponse.model_validate(product)
```

**Golang (Fiber):**
```go
func GetProduct(c *fiber.Ctx) error {
    id, err := c.ParamsInt("product_id")
    if err != nil {
        return c.Status(400).JSON(fiber.Map{"error": "Invalid ID"})
    }

    var product models.Product
    result := db.First(&product, id)

    if result.Error != nil {
        return c.Status(404).JSON(fiber.Map{"error": "Товар не найден"})
    }

    return c.JSON(ProductResponse{
        ID:    product.ID,
        Name:  product.Name,
        Price: product.Price,
        // ...
    })
}
```

### Пример 3: Bot Handler

**Python (aiogram):**
```python
@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user_id = message.from_user.id

    async with AsyncSessionFactory() as session:
        stmt = select(User).where(User.telegram_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            user = User(telegram_id=user_id, name=message.from_user.full_name)
            session.add(user)
            await session.commit()

    await message.answer("Привет!", reply_markup=get_main_keyboard())
```

**Golang (telebot):**
```go
func HandleStart(c telebot.Context) error {
    userID := c.Sender().ID

    var user models.User
    result := db.FirstOrCreate(&user, models.User{
        TelegramID: userID,
        Name:       c.Sender().FirstName,
    })

    if result.Error != nil {
        return c.Send("Ошибка сервера")
    }

    return c.Send("Привет!", GetMainKeyboard())
}

// Регистрация в main.go
bot.Handle("/start", HandleStart)
```

---

## 💡 Ключевые отличия Go vs Python

### Преимущества Go в данном проекте

1. **Производительность**
   - Telegram bot: обработка callbacks в 5-10 раз быстрее
   - API: ~100,000 RPS vs ~10,000 RPS (FastAPI)
   - Потребление памяти: 50-100MB vs 200-400MB

2. **Deployment**
   - Docker image: ~20MB (Go) vs ~200MB (Python)
   - Холодный старт: <100ms vs 2-3 секунды
   - Один бинарный файл (не нужен pip/venv)

3. **Надежность**
   - Статическая типизация (ошибки на этапе компиляции)
   - Нет runtime ImportError
   - Goroutines для concurrency (лучше asyncio)

### Недостатки Go

1. **Многословность**
   - Обработка ошибок на каждом шаге (`if err != nil`)
   - Больше boilerplate кода
   - ~1500-2000 строк Go vs 1200 строк Python (ожидаемо)

2. **Экосистема**
   - aiogram более зрелая чем telebot
   - FastAPI удобнее Fiber (автодокументация)
   - Меньше ready-made решений

3. **Время разработки**
   - Первоначальная миграция: 15-20 дней
   - Новые фичи: на 20-30% дольше разработки

---

## ⚡ Оценка трудозатрат

**Полная миграция: 15-20 рабочих дней**

| Фаза | Задачи | Время |
|------|--------|-------|
| 1. Инфраструктура | Модели, БД, конфиг, MeiliSearch | 3 дня |
| 2. REST API | Endpoints, templates, тесты | 3 дня |
| 3. Telegram Bot | Handlers, FSM, keyboards | 7 дней |
| 4. Утилиты | CSV importer | 1 день |
| 5. Docker & Deploy | Dockerfiles, тестирование | 2 дня |
| **Буфер** | Отладка, рефакторинг | 2-4 дня |

**Подход:** Можно разделить на 2 параллельных потока:
- **Поток 1 (API)**: Фаза 2 → быстрый результат для Mini App
- **Поток 2 (Bot)**: Фазы 1, 3 → основная логика

---

## 🚀 Стратегии миграции

### Вариант A: Постепенная миграция (рекомендуемый)

1. **Неделя 1-2**: Мигрировать только REST API на Go
   - Python bot продолжает работать
   - Mini App использует новый Go API
   - Минимальный риск

2. **Неделя 3-4**: Мигрировать Telegram bot на Go
   - Параллельное тестирование обеих версий
   - Переключение после полного покрытия

3. **Неделя 5**: Полное переключение на Go
   - Деплой в production
   - Удаление Python кода

**Плюсы:**
- Безопасно (можно откатиться)
- Постепенное тестирование
- Меньше downtime

**Минусы:**
- Поддержка двух кодовых баз
- Дольше общее время

### Вариант B: "Big Bang" миграция

1. Создать полностью новый Go проект
2. Мигрировать все компоненты сразу
3. Тестировать на staging
4. Переключить production одним релизом

**Плюсы:**
- Чистый код с best practices
- Быстрее достичь конечного результата

**Минусы:**
- Высокий риск
- Сложнее откат
- Возможны баги после релиза

### Вариант C: Гибридный подход (API на Go, Bot на Python)

1. Мигрировать только API на Go (Fiber)
2. Оставить bot на Python (aiogram)
3. Общая БД PostgreSQL

**Плюсы:**
- Быстрый win для API производительности
- Используем лучшее из обоих миров (aiogram очень удобная)
- Меньше работы

**Минусы:**
- Два языка в проекте
- Усложненная поддержка

---

## 📦 Финальная структура файлов

```
mdm-bot-go/
├── cmd/
│   ├── bot/
│   │   └── main.go                     # 50 строк
│   ├── api/
│   │   └── main.go                     # 40 строк
│   └── importer/
│       └── main.go                     # 100 строк
├── internal/
│   ├── config/
│   │   └── config.go                   # 60 строк
│   ├── models/
│   │   ├── user.go                     # 30 строк
│   │   ├── product.go                  # 100 строк (24 поля)
│   │   ├── cart.go                     # 25 строк
│   │   ├── favorite.go                 # 20 строк
│   │   ├── order.go                    # 50 строк
│   │   └── models.go                   # 10 строк (общие типы)
│   ├── database/
│   │   └── db.go                       # 80 строк
│   ├── search/
│   │   └── meili.go                    # 120 строк
│   ├── bot/
│   │   ├── handlers/
│   │   │   ├── start.go                # 80 строк
│   │   │   ├── callbacks.go            # 300 строк
│   │   │   ├── cart.go                 # 150 строк
│   │   │   ├── favorites.go            # 120 строк
│   │   │   ├── orders.go               # 150 строк
│   │   │   ├── profile.go              # 100 строк
│   │   │   └── search.go               # 100 строк (FSM)
│   │   ├── keyboards/
│   │   │   └── keyboards.go            # 250 строк (все builders)
│   │   └── formatters/
│   │       └── formatters.go           # 100 строк
│   └── api/
│       └── handlers.go                 # 250 строк (все endpoints)
├── migrations/                          # SQL файлы (опционально)
├── .env.example
├── .gitignore
├── go.mod
├── go.sum
├── Dockerfile.bot
├── Dockerfile.api
├── docker-compose.yml
├── README.md
└── GOLANG_MIGRATION_PLAN.md            # этот файл

Итого: ~2100-2300 строк Go кода (vs 1200 Python)
```

---

## 🧪 Тестирование

### Unit Tests

```go
// internal/models/user_test.go
func TestUserCreation(t *testing.T) {
    db := setupTestDB()

    user := &User{
        TelegramID: 123456,
        Name: "Test User",
    }

    result := db.Create(user)
    assert.NoError(t, result.Error)
    assert.NotZero(t, user.TelegramID)
}
```

### Integration Tests

```go
// internal/api/handlers_test.go
func TestGetProducts(t *testing.T) {
    app := setupTestApp()

    req := httptest.NewRequest("GET", "/api/products?page=1&limit=10", nil)
    resp, _ := app.Test(req)

    assert.Equal(t, 200, resp.StatusCode)
}
```

### Benchmark Tests

```go
func BenchmarkSearchProducts(b *testing.B) {
    client := setupMeiliClient()

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        client.SearchProducts("тест", 10)
    }
}
```

---

## 📊 Ожидаемые метрики

### До миграции (Python)
- **Потребление памяти**: Bot ~300MB, API ~200MB
- **Docker image**: Bot ~350MB, API ~300MB
- **Время старта**: 3-5 секунд
- **Latency API**: p95 ~50ms (локально)
- **Throughput**: ~1000 req/sec

### После миграции (Go)
- **Потребление памяти**: Bot ~80MB, API ~50MB ✅ **-75%**
- **Docker image**: Bot ~25MB, API ~20MB ✅ **-93%**
- **Время старта**: <100ms ✅ **-97%**
- **Latency API**: p95 ~5ms ✅ **-90%**
- **Throughput**: ~50,000 req/sec ✅ **+4900%**

---

## ✅ Рекомендации

### Для вашего случая (стратегический переход на Go):

1. **Начните с Варианта A (постепенная миграция)**
   - Меньше риска
   - Проще учиться на ходу
   - Можно откатиться

2. **Первый шаг: REST API**
   - Проще всего для начала
   - Быстрый результат (3 дня)
   - Получите опыт работы с Fiber + GORM

3. **Второй шаг: CSV Importer**
   - Standalone утилита
   - Хороший practice для работы с БД

4. **Финальный шаг: Telegram Bot**
   - Самая сложная часть (FSM, keyboards)
   - Можете параллельно поддерживать Python версию

5. **Документация и best practices**
   - Используйте официальные примеры библиотек
   - Структура проекта: https://github.com/golang-standards/project-layout
   - Стиль кода: `gofmt`, `golangci-lint`

---

## 🔗 Полезные ссылки

### Документация библиотек
- telebot: https://github.com/tucnak/telebot
- GORM: https://gorm.io/docs/
- Fiber: https://docs.gofiber.io/
- Viper: https://github.com/spf13/viper
- MeiliSearch Go: https://github.com/meilisearch/meilisearch-go

### Примеры проектов
- Telegram Bot с telebot: https://github.com/tucnak/telebot/tree/v3/examples
- Fiber REST API: https://github.com/gofiber/recipes
- GORM примеры: https://github.com/go-gorm/gorm/tree/master/examples

### Обучающие материалы
- Go by Example: https://gobyexample.com/
- Effective Go: https://go.dev/doc/effective_go
- Awesome Go: https://github.com/avelino/awesome-go

---

## 📝 Заметки

- Этот план рассчитан на ~15-20 дней **активной** разработки
- При первом опыте с Go добавьте +30-50% времени на обучение
- Используйте параллельную разработку (API + Bot одновременно)
- Обязательно пишите тесты сразу (в Go это проще чем в Python)
- Применяйте `go fmt` и `golangci-lint` для качества кода

---

**Создано**: 2025-12-30
**Версия**: 1.0
**Автор**: Migration plan для MDM Bot Python → Golang
