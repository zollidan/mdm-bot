<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppHeader from '../components/AppHeader.vue'

interface Product {
  id: number
  name: string
  price: number
  vendor_code?: string
  image?: string
}

interface ApiResponse {
  items: Product[]
  total: number
  total_pages: number
  page: number
}

const products = ref<Product[]>([])
const isLoading = ref(true)
const hasError = ref(false)
const searchQuery = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const cartCount = ref(0)
const limit = 10
let searchTimeout: number | undefined

const loadProducts = async (page: number = 1) => {
  currentPage.value = page
  isLoading.value = true

  try {
    const response = await fetch(`/api/products?page=${page}&limit=${limit}`)
    const data: ApiResponse = await response.json()

    products.value = data.items
    totalPages.value = data.total_pages
    isLoading.value = false

    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (error) {
    console.error('Ошибка загрузки:', error)
    hasError.value = true
    isLoading.value = false
  }
}

const handleSearch = async () => {
  const query = searchQuery.value.trim()

  if (query.length === 0) {
    loadProducts(1)
    return
  }

  if (query.length < 2) return

  isLoading.value = true

  try {
    const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&limit=20`)
    const data: ApiResponse = await response.json()

    products.value = data.items
    isLoading.value = false
  } catch (error) {
    console.error('Ошибка поиска:', error)
    hasError.value = true
    isLoading.value = false
  }
}

const onSearchInput = () => {
  clearTimeout(searchTimeout)
  searchTimeout = window.setTimeout(() => {
    handleSearch()
  }, 300)
}

const addToCart = () => {
  cartCount.value++

  // Telegram Haptic Feedback
  if (window.Telegram && window.Telegram.WebApp) {
    window.Telegram.WebApp.HapticFeedback.impactOccurred('medium')
  }
}

const getPaginationButtons = () => {
  const buttons = []
  const start = Math.max(1, currentPage.value - 1)
  const end = Math.min(totalPages.value, currentPage.value + 1)

  for (let i = start; i <= end; i++) {
    buttons.push(i)
  }

  return buttons
}

onMounted(() => {
  loadProducts(1)
})
</script>

<template>
  <div>
    <AppHeader title="каталог" back-link="/" :show-cart="true" :cart-count="cartCount" />

    <main>
      <!-- Search & Filter Bar -->
      <section>
        <div>
          <input
            v-model="searchQuery"
            @input="onSearchInput"
            type="text"
            placeholder="поиск по названию..."
          />
          <div>
            🔍
          </div>
        </div>

        <!-- Category Filters (placeholder) -->
        <div>
          <button>
            все
          </button>
          <button>
            одежда
          </button>
          <button>
            обувь
          </button>
          <button>
            аксессуары
          </button>
        </div>
      </section>

      <!-- Product Grid -->
      <div>
        <!-- Loading State -->
        <div v-if="isLoading">
          <p>наполняем полки...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="hasError">
          <p>Ошибка загрузки. Попробуйте обновить страницу.</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="products.length === 0">
          <p>Ничего не нашли 🕵️‍♂️</p>
        </div>

        <!-- Products -->
        <div v-else v-for="(product, index) in products" :key="product.id">
          <router-link :to="`/products/${product.id}`">
            <img
              v-if="product.image"
              :src="product.image"
              :alt="product.name"
            />
            <div v-else>📦</div>
            <div>
              new
            </div>
          </router-link>

          <div>
            <h3>{{ product.name }}</h3>
            <div>
              <span>{{ product.price.toLocaleString() }} ₽</span>
              <button @click="addToCart">
                купить
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="!searchQuery && !isLoading && products.length > 0">
        <!-- Previous Button -->
        <button v-if="currentPage > 1" @click="loadProducts(currentPage - 1)">
          ‹
        </button>

        <!-- Page Numbers -->
        <button
          v-for="page in getPaginationButtons()"
          :key="page"
          @click="loadProducts(page)"
        >
          {{ page }}
        </button>

        <!-- Next Button -->
        <button v-if="currentPage < totalPages" @click="loadProducts(currentPage + 1)">
          ›
        </button>
      </div>

      <!-- Search Results Counter -->
      <div v-else-if="searchQuery && !isLoading">
        <p>Найдено: {{ products.length }} товаров</p>
      </div>
    </main>
  </div>
</template>

