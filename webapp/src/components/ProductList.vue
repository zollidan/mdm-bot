<template>
  <div class="container">
    <div v-if="loading" class="loading">
      Загрузка...
    </div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <div v-else>
      <div class="product-grid">
        <div
          v-for="product in products"
          :key="product.id"
          class="product-card"
          @click="handleProductClick(product)"
        >
          <img
            v-if="product.image"
            :src="product.image"
            :alt="product.name"
            class="product-image"
            @error="handleImageError"
          >
          <div v-else class="product-image"></div>

          <div class="product-info">
            <div class="product-name">{{ product.name }}</div>
            <div class="product-price">{{ formatPrice(product.price) }} ₽</div>
          </div>
        </div>
      </div>

      <div class="pagination">
        <button
          @click="previousPage"
          :disabled="currentPage === 1"
        >
          ← Назад
        </button>

        <span class="pagination-info">
          Страница {{ currentPage }} из {{ totalPages }}
        </span>

        <button
          @click="nextPage"
          :disabled="currentPage >= totalPages"
        >
          Вперёд →
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { getProducts } from '../api/products'

export default {
  name: 'ProductList',
  setup() {
    const products = ref([])
    const loading = ref(false)
    const error = ref(null)
    const currentPage = ref(1)
    const totalPages = ref(1)
    const itemsPerPage = 20

    const loadProducts = async () => {
      loading.value = true
      error.value = null

      try {
        const data = await getProducts(currentPage.value, itemsPerPage)
        products.value = data.items
        totalPages.value = data.total_pages

        // Прокрутка вверх при смене страницы
        window.scrollTo({ top: 0, behavior: 'smooth' })
      } catch (err) {
        error.value = 'Ошибка загрузки товаров. Попробуйте позже.'
        console.error(err)
      } finally {
        loading.value = false
      }
    }

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
        loadProducts()
      }
    }

    const previousPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
        loadProducts()
      }
    }

    const formatPrice = (price) => {
      return new Intl.NumberFormat('ru-RU').format(price)
    }

    const handleProductClick = (product) => {
      // Отправляем событие в Telegram бот
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.sendData(JSON.stringify({
          action: 'view_product',
          product_id: product.id
        }))
      }
    }

    const handleImageError = (event) => {
      event.target.style.display = 'none'
    }

    onMounted(() => {
      loadProducts()
    })

    return {
      products,
      loading,
      error,
      currentPage,
      totalPages,
      nextPage,
      previousPage,
      formatPrice,
      handleProductClick,
      handleImageError
    }
  }
}
</script>
