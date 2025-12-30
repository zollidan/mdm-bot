<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '../components/AppHeader.vue'

interface Product {
  id: number
  name: string
  price: number
  vendor_code?: string
  image?: string
  description?: string
}

const route = useRoute()
const product = ref<Product | null>(null)
const isLoading = ref(true)
const hasError = ref(false)
const quantity = ref(1)
const cartCount = ref(0)

const loadProductDetails = async () => {
  const productId = route.params.id

  try {
    const response = await fetch(`/api/products/${productId}`)

    if (!response.ok) {
      throw new Error('Product not found')
    }

    product.value = await response.json()
    isLoading.value = false
  } catch (error) {
    console.error('Ошибка загрузки:', error)
    hasError.value = true
    isLoading.value = false
  }
}

const changeQuantity = (delta: number) => {
  quantity.value = Math.max(1, quantity.value + delta)

  // Haptic feedback for Telegram
  if (window.Telegram && window.Telegram.WebApp) {
    window.Telegram.WebApp.HapticFeedback.impactOccurred('light')
  }
}

const addToCart = (event: Event) => {
  cartCount.value += quantity.value

  // Visual feedback
  const btn = event.target as HTMLButtonElement
  const originalText = btn.innerText
  btn.innerText = '✓ ДОБАВЛЕНО'
  btn.classList.add('bg-green-400')

  setTimeout(() => {
    btn.innerText = originalText
    btn.classList.remove('bg-green-400')
  }, 1500)

  // Haptic feedback
  if (window.Telegram && window.Telegram.WebApp) {
    window.Telegram.WebApp.HapticFeedback.notificationOccurred('success')
  }

  // Reset quantity
  quantity.value = 1
}

const buyNow = () => {
  // Placeholder for buy now functionality
  if (window.Telegram && window.Telegram.WebApp) {
    window.Telegram.WebApp.HapticFeedback.impactOccurred('heavy')
    window.Telegram.WebApp.showAlert('Функция быстрой покупки в разработке!')
  } else {
    alert('Функция быстрой покупки в разработке!')
  }
}

onMounted(() => {
  loadProductDetails()
})
</script>

<template>
  <div>
    <AppHeader title="назад" back-link="/products" :show-cart="true" :cart-count="cartCount" />

    <main>
      <!-- Loading State -->
      <div v-if="isLoading">
        <div>
          <p>загружаем...</p>
        </div>
        <div></div>
      </div>

      <!-- Error State -->
      <div v-else-if="hasError">
        <p>😞</p>
        <p>Товар не найден</p>
        <router-link to="/products">
          вернуться в каталог
        </router-link>
      </div>

      <!-- Product Details -->
      <template v-else-if="product">
        <!-- Product Image -->
        <div>
          <img
            v-if="product.image"
            :src="product.image"
            :alt="product.name"
          />
          <div v-else>
            <span>📦</span>
          </div>
        </div>

        <!-- Product Info Card -->
        <div>
          <!-- Vendor Code Badge -->
          <div v-if="product.vendor_code">
            art: {{ product.vendor_code }}
          </div>

          <!-- Product Name -->
          <h2>{{ product.name }}</h2>

          <!-- Description -->
          <div v-if="product.description">
            <p>описание</p>
            <p>{{ product.description }}</p>
          </div>

          <!-- Price & Actions -->
          <div>
            <div>
              <span>цена</span>
              <span>{{ product.price.toLocaleString() }} ₽</span>
            </div>

            <!-- Quantity Selector -->
            <div>
              <button @click="changeQuantity(-1)">
                −
              </button>
              <div>
                <span>{{ quantity }}</span>
                <span>шт</span>
              </div>
              <button @click="changeQuantity(1)">
                +
              </button>
            </div>

            <!-- Add to Cart Button -->
            <button @click="addToCart">
              добавить в корзину
            </button>

            <!-- Buy Now Button -->
            <button @click="buyNow">
              купить сейчас →
            </button>
          </div>
        </div>

        <!-- Additional Info -->
        <div>
          <div>
            <p>
              доставка
            </p>
            <p>БЕСПЛАТНО</p>
          </div>
          <div>
            <p>
              гарантия
            </p>
            <p>1 ГОД</p>
          </div>
        </div>
      </template>
    </main>
  </div>
</template>
