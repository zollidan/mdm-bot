# План миграции MDM Bot: Гибридная архитектура Vue.js + Telegram Bot

## 📋 Концепция

**Гибридная архитектура:**
- 🤖 **Telegram Bot** (main.py) - Приветствие, регистрация, точка входа в Mini App
- 🌐 **Vue.js Mini App** - Весь основной функционал (каталог, корзина, заказы, профиль)
- ⚡ **FastAPI** (api_server.py) - REST API для фронтенда

### Разделение ответственности

#### Остается в Telegram Bot (main.py)
```
✅ /start - Приветственное сообщение
✅ Создание/обновление пользователя в БД
✅ Кнопка "Открыть каталог" → запуск Mini App
✅ Базовые команды помощи
```

#### Переносится в Vue.js Mini App
```
🔄 Каталог товаров с пагинацией
🔄 Детальная страница товара
🔄 Поиск товаров (MeiliSearch)
🔄 Корзина с управлением количеством
🔄 Избранное
🔄 Оформление заказа
🔄 История заказов
🔄 Профиль пользователя
🔄 Отзывы
```

---

## 🎯 Этап 1: Backend API (FastAPI)

### 1.1 Аутентификация через Telegram Web App

**Файл:** `api_server.py`

**Новые зависимости:**
```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

**Эндпоинты аутентификации:**
```python
POST /api/auth/telegram
  Body: { initData: string }
  Validates: Telegram Web App initData signature
  Response: { user: UserResponse, token: string }

GET /api/auth/me
  Headers: Authorization: Bearer <token>
  Response: UserResponse
```

**Pydantic модели:**
```python
class UserResponse(BaseModel):
    telegram_id: int
    username: Optional[str]
    name: str
    phone_number: str
    address: str
    created_date: datetime

    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    user: UserResponse
    token: str
    token_type: str = "bearer"
```

### 1.2 Товары и каталог

**Эндпоинты:**
```python
# ✅ Уже реализовано
GET /api/products?page=1&limit=20
GET /api/products/{id}

# 🆕 Нужно добавить
GET /api/products/search?q={query}&page=1&limit=20
  Response: ProductsListResponse (через MeiliSearch)

GET /api/products/{id}/full
  Response: ProductDetailResponse (все поля из models.py)
```

**Расширенная модель товара:**
```python
class ProductDetailResponse(ProductResponse):
    vendor: str
    model: str
    vendor_code: str
    availability: str
    stock_chashnikovo: Optional[str]
    stock_kantemirovskaya: Optional[str]
    stock_spb: Optional[str]
    # ... остальные склады
    manufacturer_warranty: bool
    unit: str
```

### 1.3 Корзина

**Эндпоинты:**
```python
GET /api/cart
  Response: CartResponse

POST /api/cart
  Body: { product_id: int, quantity: int }
  Response: CartItemResponse

PATCH /api/cart/{item_id}
  Body: { quantity: int }
  Response: CartItemResponse

DELETE /api/cart/{item_id}
  Response: { message: "deleted" }

DELETE /api/cart
  Response: { message: "cart cleared" }
```

**Pydantic модели:**
```python
class CartItemResponse(BaseModel):
    id: int
    product: ProductResponse
    quantity: int
    added_date: datetime
    subtotal: float  # price * quantity

class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total_sum: float
    total_items: int
```

### 1.4 Избранное

**Эндпоинты:**
```python
GET /api/favorites
  Response: List[ProductResponse]

POST /api/favorites
  Body: { product_id: int }
  Response: { message: "added" }

DELETE /api/favorites/{product_id}
  Response: { message: "removed" }

GET /api/favorites/check?ids=1,2,3
  Response: { "1": true, "2": false, "3": true }
```

### 1.5 Заказы

**Эндпоинты:**
```python
POST /api/orders
  Body: { delivery_method?: string, payment_method?: string }
  Response: OrderResponse

GET /api/orders?page=1&limit=20
  Response: { items: OrderResponse[], total: int, page: int, total_pages: int }

GET /api/orders/{id}
  Response: OrderDetailResponse

POST /api/orders/{id}/repeat
  Response: { message: "added to cart", items_added: int }
```

**Pydantic модели:**
```python
class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    product_image: Optional[str]
    quantity: int
    price: float
    subtotal: float

class OrderResponse(BaseModel):
    id: int
    total_sum: float
    status: str
    order_date: datetime
    items_count: int

class OrderDetailResponse(OrderResponse):
    delivery_method: Optional[str]
    payment_method: Optional[str]
    tracking_number: Optional[str]
    order_items: List[OrderItemResponse]
    user_name: str
    user_phone: str
    user_address: str
```

### 1.6 Профиль пользователя

**Эндпоинты:**
```python
GET /api/user/stats
  Response: UserStatsResponse

PATCH /api/user/profile
  Body: { name?, phone_number?, address? }
  Response: UserResponse
```

**Pydantic модели:**
```python
class UserStatsResponse(BaseModel):
    cart_items: int
    favorites_count: int
    orders_count: int
    reviews_count: int
    total_spent: float
    days_since_registration: int
```

### 1.7 Отзывы (опционально, Priority 2)

**Эндпоинты:**
```python
GET /api/products/{id}/reviews
  Response: List[ReviewResponse]

POST /api/reviews
  Body: { product_id: int, rating: int, text: string }
  Response: ReviewResponse
```

---

## 🎨 Этап 2: Frontend (Vue.js)

### 2.1 Структура проекта

```
webapp/src/
├── main.js
├── App.vue
├── router/
│   └── index.js              # Vue Router
├── stores/
│   ├── auth.js               # Аутентификация, пользователь
│   ├── cart.js               # Корзина
│   ├── favorites.js          # Избранное
│   └── products.js           # Кэш товаров
├── api/
│   ├── client.js             # Axios instance с auth
│   ├── auth.js
│   ├── products.js
│   ├── cart.js
│   ├── favorites.js
│   ├── orders.js
│   └── user.js
├── views/
│   ├── HomeView.vue          # 🏠 Главная (Dashboard)
│   ├── CatalogView.vue       # 📦 Каталог
│   ├── ProductView.vue       # 📦 Детали товара
│   ├── SearchView.vue        # 🔍 Поиск
│   ├── CartView.vue          # 🛒 Корзина
│   ├── CheckoutView.vue      # 💳 Оформление заказа
│   ├── FavoritesView.vue     # ⭐ Избранное
│   ├── OrdersView.vue        # 📦 История заказов
│   ├── OrderDetailView.vue   # 📦 Детали заказа
│   ├── ProfileView.vue       # 👤 Профиль
│   └── HelpView.vue          # ❓ Помощь
├── components/
│   ├── layout/
│   │   ├── AppNavbar.vue     # Нижняя навигация
│   │   └── AppHeader.vue     # Шапка с поиском
│   ├── product/
│   │   ├── ProductCard.vue
│   │   ├── ProductGrid.vue
│   │   └── ProductGallery.vue
│   ├── cart/
│   │   ├── CartItem.vue
│   │   └── CartSummary.vue
│   ├── order/
│   │   └── OrderCard.vue
│   └── common/
│       ├── LoadingSpinner.vue
│       ├── EmptyState.vue
│       ├── Pagination.vue
│       └── QuantitySelector.vue
└── utils/
    ├── telegram.js           # Telegram Web App SDK
    ├── format.js             # Форматирование
    └── validation.js         # Валидация
```

### 2.2 Установка зависимостей

```bash
cd webapp
npm install vue-router@4 pinia axios @vueuse/core
```

### 2.3 Vue Router (router/index.js)

```javascript
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/catalog',
    name: 'catalog',
    component: () => import('@/views/CatalogView.vue')
  },
  {
    path: '/product/:id',
    name: 'product',
    component: () => import('@/views/ProductView.vue')
  },
  {
    path: '/search',
    name: 'search',
    component: () => import('@/views/SearchView.vue')
  },
  {
    path: '/cart',
    name: 'cart',
    component: () => import('@/views/CartView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/checkout',
    name: 'checkout',
    component: () => import('@/views/CheckoutView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/favorites',
    name: 'favorites',
    component: () => import('@/views/FavoritesView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/orders',
    name: 'orders',
    component: () => import('@/views/OrdersView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/orders/:id',
    name: 'order-detail',
    component: () => import('@/views/OrderDetailView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/help',
    name: 'help',
    component: () => import('@/views/HelpView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Пытаемся авторизоваться через Telegram
    authStore.initAuth().then(() => {
      next()
    }).catch(() => {
      next('/') // Или показать ошибку
    })
  } else {
    next()
  }
})

export default router
```

### 2.4 Pinia Stores

**stores/auth.js:**
```javascript
import { defineStore } from 'pinia'
import { authApi } from '@/api/auth'
import { initTelegramWebApp, getTelegramInitData } from '@/utils/telegram'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    isAuthenticated: false,
    stats: null
  }),

  getters: {
    userName: (state) => state.user?.name || 'Гость',
    userPhone: (state) => state.user?.phone_number,
    isProfileComplete: (state) => {
      return state.user?.name && state.user?.phone_number && state.user?.address
    }
  },

  actions: {
    async initAuth() {
      try {
        initTelegramWebApp()
        const initData = getTelegramInitData()

        const response = await authApi.authenticate(initData)
        this.user = response.user
        this.token = response.token
        this.isAuthenticated = true

        localStorage.setItem('token', response.token)
      } catch (error) {
        console.error('Auth failed:', error)
        throw error
      }
    },

    async fetchProfile() {
      const response = await authApi.getMe()
      this.user = response
    },

    async updateProfile(data) {
      const response = await authApi.updateProfile(data)
      this.user = response
    },

    async fetchStats() {
      const response = await authApi.getStats()
      this.stats = response
    },

    logout() {
      this.user = null
      this.token = null
      this.isAuthenticated = false
      localStorage.removeItem('token')
    }
  }
})
```

**stores/cart.js:**
```javascript
import { defineStore } from 'pinia'
import { cartApi } from '@/api/cart'

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: [],
    totalSum: 0,
    loading: false
  }),

  getters: {
    itemCount: (state) => state.items.reduce((sum, item) => sum + item.quantity, 0),
    isEmpty: (state) => state.items.length === 0
  },

  actions: {
    async fetchCart() {
      this.loading = true
      try {
        const response = await cartApi.getCart()
        this.items = response.items
        this.totalSum = response.total_sum
      } finally {
        this.loading = false
      }
    },

    async addItem(productId, quantity = 1) {
      const item = await cartApi.addToCart(productId, quantity)
      await this.fetchCart() // Reload cart
      return item
    },

    async updateQuantity(itemId, quantity) {
      await cartApi.updateQuantity(itemId, quantity)
      await this.fetchCart()
    },

    async removeItem(itemId) {
      await cartApi.removeFromCart(itemId)
      await this.fetchCart()
    },

    async clearCart() {
      await cartApi.clearCart()
      this.items = []
      this.totalSum = 0
    }
  }
})
```

**stores/favorites.js:**
```javascript
import { defineStore } from 'pinia'
import { favoritesApi } from '@/api/favorites'

export const useFavoritesStore = defineStore('favorites', {
  state: () => ({
    items: [],
    favoriteIds: new Set()
  }),

  getters: {
    isFavorite: (state) => (productId) => state.favoriteIds.has(productId),
    count: (state) => state.items.length
  },

  actions: {
    async fetchFavorites() {
      const items = await favoritesApi.getFavorites()
      this.items = items
      this.favoriteIds = new Set(items.map(item => item.id))
    },

    async toggleFavorite(productId) {
      if (this.isFavorite(productId)) {
        await favoritesApi.removeFromFavorites(productId)
        this.favoriteIds.delete(productId)
        this.items = this.items.filter(item => item.id !== productId)
      } else {
        await favoritesApi.addToFavorites(productId)
        this.favoriteIds.add(productId)
        await this.fetchFavorites()
      }
    }
  }
})
```

### 2.5 API клиенты

**api/client.js:**
```javascript
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor: добавляем токен
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor: обработка ошибок
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      // Redirect to login or show error
    }
    return Promise.reject(error)
  }
)

export default apiClient
```

**api/cart.js:**
```javascript
import apiClient from './client'

export const cartApi = {
  async getCart() {
    const { data } = await apiClient.get('/cart')
    return data
  },

  async addToCart(productId, quantity) {
    const { data } = await apiClient.post('/cart', { product_id: productId, quantity })
    return data
  },

  async updateQuantity(itemId, quantity) {
    const { data } = await apiClient.patch(`/cart/${itemId}`, { quantity })
    return data
  },

  async removeFromCart(itemId) {
    const { data } = await apiClient.delete(`/cart/${itemId}`)
    return data
  },

  async clearCart() {
    const { data } = await apiClient.delete('/cart')
    return data
  }
}
```

### 2.6 Telegram Web App утилиты

**utils/telegram.js:**
```javascript
export function initTelegramWebApp() {
  if (window.Telegram?.WebApp) {
    const tg = window.Telegram.WebApp
    tg.ready()
    tg.expand()

    // Apply Telegram theme
    applyTelegramTheme(tg.themeParams)

    return tg
  }
  return null
}

export function getTelegramInitData() {
  return window.Telegram?.WebApp?.initData || ''
}

export function getTelegramUser() {
  return window.Telegram?.WebApp?.initDataUnsafe?.user || null
}

export function applyTelegramTheme(themeParams) {
  const root = document.documentElement

  root.style.setProperty('--tg-bg-color', themeParams.bg_color || '#ffffff')
  root.style.setProperty('--tg-text-color', themeParams.text_color || '#000000')
  root.style.setProperty('--tg-hint-color', themeParams.hint_color || '#999999')
  root.style.setProperty('--tg-link-color', themeParams.link_color || '#2481cc')
  root.style.setProperty('--tg-button-color', themeParams.button_color || '#2481cc')
  root.style.setProperty('--tg-button-text-color', themeParams.button_text_color || '#ffffff')
}

export function closeTelegramWebApp() {
  window.Telegram?.WebApp?.close()
}

export function showTelegramBackButton(onClick) {
  const tg = window.Telegram?.WebApp
  if (tg) {
    tg.BackButton.show()
    tg.BackButton.onClick(onClick)
  }
}

export function hideTelegramBackButton() {
  window.Telegram?.WebApp?.BackButton.hide()
}
```

---

## 📋 Этап 3: Упрощенный Telegram Bot (main.py)

### 3.1 Что остается в боте

**Минимальный функционал:**

```python
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import CommandStart
from sqlalchemy import select
from database import AsyncSessionFactory
from models import User
from config import settings

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: Message):
    """Приветствие и создание/обновление пользователя"""
    async with AsyncSessionFactory() as session:
        # Проверяем существует ли пользователь
        query = select(User).where(User.telegram_id == message.from_user.id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            # Создаем нового пользователя
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username or "",
                name=message.from_user.first_name or "Пользователь",
                phone_number="",  # Будет заполнено в профиле Mini App
                address=""  # Будет заполнено в профиле Mini App
            )
            session.add(user)
            await session.commit()

            greeting = f"👋 Привет, {user.name}!\n\n"
            greeting += "Добро пожаловать в магазин MDM!\n\n"
            greeting += "🛍️ Нажми кнопку ниже, чтобы открыть каталог товаров."
        else:
            greeting = f"👋 С возвращением, {user.name}!\n\n"
            greeting += "🛍️ Открой каталог, чтобы продолжить покупки."

    # Создаем кнопку с Mini App
    webapp_button = KeyboardButton(
        text="🛍️ Открыть каталог",
        web_app=WebAppInfo(url=settings.WEBAPP_URL)
    )

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[webapp_button]],
        resize_keyboard=True
    )

    await message.answer(greeting, reply_markup=keyboard)

@dp.message(F.text == "/help")
async def cmd_help(message: Message):
    """Помощь"""
    help_text = """
❓ <b>Помощь</b>

🛍️ <b>Как сделать заказ:</b>
1. Нажми "Открыть каталог"
2. Выбери товары и добавь в корзину
3. Перейди в корзину и оформи заказ

📞 <b>Поддержка:</b>
Телефон: +7 (123) 456-78-90
Email: support@mdm-shop.ru
Telegram: @mdm_support

🕐 <b>Время работы:</b>
Пн-Пт: 9:00 - 18:00
Сб-Вс: Выходной
"""
    await message.answer(help_text, parse_mode="HTML")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**Что удаляем из main.py:**
- ❌ Все FSM состояния (SearchForm, ProfileForm)
- ❌ Обработчики поиска
- ❌ Обработчики корзины
- ❌ Обработчики избранного
- ❌ Обработчики заказов
- ❌ Обработчики профиля
- ❌ Все inline клавиатуры (kbs.py больше не нужен)

---

## 🚀 Этап 4: Пошаговый план реализации

### Week 1: Backend Foundation

**День 1-2: Аутентификация**
- [ ] Установить зависимости (python-jose, passlib)
- [ ] Реализовать валидацию Telegram initData
- [ ] Создать JWT токены
- [ ] Эндпоинт `POST /api/auth/telegram`
- [ ] Middleware для авторизации
- [ ] Протестировать через Postman

**День 3-4: API для товаров**
- [ ] Расширить ProductResponse (добавить все поля)
- [ ] Эндпоинт поиска `GET /api/products/search` (MeiliSearch)
- [ ] Эндпоинт детальной информации `GET /api/products/{id}/full`

**День 5-7: API для корзины и избранного**
- [ ] CRUD эндпоинты для корзины
- [ ] CRUD эндпоинты для избранного
- [ ] Pydantic модели
- [ ] Обработка ошибок (товар не найден, и т.д.)

### Week 2: Backend Orders & User

**День 1-3: API для заказов**
- [ ] `POST /api/orders` - создание заказа
- [ ] `GET /api/orders` - список заказов
- [ ] `GET /api/orders/{id}` - детали заказа
- [ ] `POST /api/orders/{id}/repeat` - повторить заказ
- [ ] Расчет итоговых сумм
- [ ] Очистка корзины после заказа

**День 4-5: API для профиля**
- [ ] `GET /api/user/stats` - статистика
- [ ] `PATCH /api/user/profile` - обновление профиля
- [ ] Валидация телефона (regex)

**День 6-7: Тестирование Backend**
- [ ] Протестировать все эндпоинты
- [ ] Обработка edge cases
- [ ] Документация API (Swagger)

### Week 3: Frontend Core

**День 1-2: Настройка проекта**
- [ ] Установить зависимости (vue-router, pinia, axios)
- [ ] Настроить Vue Router
- [ ] Создать базовую структуру папок
- [ ] Настроить Pinia stores
- [ ] Создать API клиенты

**День 3-4: Аутентификация и Layout**
- [ ] Telegram Web App инициализация
- [ ] Auth store (initAuth, fetchProfile)
- [ ] AppNavbar компонент (нижняя навигация)
- [ ] AppHeader компонент (поиск)
- [ ] Navigation guard

**День 5-7: Главная и каталог**
- [ ] HomeView (dashboard с статистикой)
- [ ] Улучшить CatalogView (фильтры, сортировка)
- [ ] ProductCard компонент
- [ ] ProductGrid компонент
- [ ] Pagination компонент

### Week 4: Frontend Products & Cart

**День 1-3: Детальная страница товара**
- [ ] ProductView компонент
- [ ] ProductGallery (изображения)
- [ ] Характеристики товара
- [ ] Кнопки "В корзину", "В избранное"
- [ ] Отображение наличия на складах

**День 4-7: Корзина**
- [ ] CartView
- [ ] CartItem компонент
- [ ] QuantitySelector компонент
- [ ] CartSummary (итоговая сумма)
- [ ] Интеграция с cart store
- [ ] Анимации добавления в корзину

### Week 5: Frontend Orders & Profile

**День 1-3: Оформление заказа**
- [ ] CheckoutView
- [ ] Проверка профиля
- [ ] Форма недостающих данных
- [ ] Подтверждение заказа
- [ ] Успешное оформление (конфетти?)

**День 4-5: История заказов**
- [ ] OrdersView
- [ ] OrderCard компонент
- [ ] OrderDetailView
- [ ] Кнопка "Повторить заказ"

**День 6-7: Профиль**
- [ ] ProfileView
- [ ] Форма редактирования (имя, телефон, адрес)
- [ ] Валидация телефона
- [ ] Отображение статистики

### Week 6: Frontend Additional Features

**День 1-2: Избранное**
- [ ] FavoritesView
- [ ] Интеграция с favorites store
- [ ] Toggle избранное на карточках
- [ ] EmptyState компонент

**День 3-4: Поиск**
- [ ] SearchView
- [ ] SearchBar компонент в AppHeader
- [ ] Интеграция с MeiliSearch API
- [ ] История поиска (localStorage)

**День 5-7: UX улучшения**
- [ ] LoadingSpinner во всех views
- [ ] EmptyState для пустых списков
- [ ] Toast уведомления (успех, ошибка)
- [ ] Плавные переходы между страницами
- [ ] Pull-to-refresh (опционально)

### Week 7: Polish & Deploy

**День 1-3: Упрощение бота**
- [ ] Очистить main.py (оставить только /start и /help)
- [ ] Удалить kbs.py
- [ ] Удалить utils.py
- [ ] Удалить FSM формы
- [ ] Тестирование бота

**День 4-5: Docker и деплой**
- [ ] Обновить docker-compose.yml
- [ ] Nginx конфигурация
- [ ] Build Vue.js приложения
- [ ] Тестирование на staging

**День 6-7: Финальное тестирование**
- [ ] E2E тесты основных флоу
- [ ] Тестирование на мобильных устройствах
- [ ] Исправление багов
- [ ] Документация

---

## 📊 Приоритизация функций

### Must Have (Обязательно для MVP)
1. ✅ Аутентификация через Telegram
2. ✅ Каталог товаров с пагинацией
3. ✅ Детальная страница товара
4. ✅ Корзина с управлением количеством
5. ✅ Оформление заказа
6. ✅ История заказов
7. ✅ Профиль пользователя

### Should Have (Желательно)
1. ⭐ Избранное
2. 🔍 Поиск товаров
3. 📱 Адаптивный дизайн
4. 🎨 Telegram тема

### Nice to Have (Опционально)
1. ⭐ Отзывы и рейтинги
2. 🏷️ Категории товаров
3. 📊 Расширенная аналитика
4. 🔔 Уведомления

---

## 📁 Файловая структура (итоговая)

```
mdm-bot/
├── main.py                    # ✂️ Упрощенный бот (только /start, /help)
├── api_server.py              # 🚀 Полный REST API
├── models.py                  # (без изменений)
├── database.py                # (без изменений)
├── config.py                  # (без изменений)
├── meilisearch_client.py      # (без изменений)
├── ❌ kbs.py                  # УДАЛИТЬ
├── ❌ utils.py                # УДАЛИТЬ
├── webapp/
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/
│   │   ├── stores/
│   │   ├── api/
│   │   ├── views/
│   │   ├── components/
│   │   └── utils/
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml         # (обновить)
└── VUE_MIGRATION_PLAN.md      # Этот файл
```

---

## 🎯 Метрики успеха

### Функциональные
- ✅ 100% основных функций из FEATURES.md реализовано в Vue
- ✅ Бот упрощен до минимума (приветствие + кнопка Mini App)
- ✅ Все данные сохраняются в PostgreSQL

### Технические
- ⚡ Загрузка главной страницы < 2 сек
- 📱 Работает на всех мобильных устройствах
- 🔒 Безопасная JWT авторизация
- 🎨 Использует Telegram тему

### UX
- 🚀 Плавная навигация без перезагрузок
- ✨ Анимации добавления в корзину
- 📊 Прозрачная статистика
- 💬 Понятные сообщения об ошибках

---

## 🛠️ Следующие шаги

### 1. Начать с Backend аутентификации

```bash
# Установить зависимости
pip install python-jose[cryptography] passlib[bcrypt]

# Создать файл auth.py с функциями валидации
# Добавить эндпоинты в api_server.py
```

### 2. Настроить Frontend структуру

```bash
cd webapp
npm install vue-router pinia axios @vueuse/core

# Создать папки stores/, api/, views/, components/
# Настроить router/index.js
```

### 3. Реализовать аутентификацию end-to-end

```
Telegram Bot (/start)
  → Кнопка "Открыть каталог"
  → Vue.js инициализация
  → POST /api/auth/telegram
  → JWT токен
  → Сохранение в localStorage
```

---

**Готов начать?** Скажи с чего начнем! 🚀

Предлагаю начать с:
1. Backend аутентификации (api_server.py)
2. Frontend auth store (stores/auth.js)
3. Упрощение бота (main.py)
