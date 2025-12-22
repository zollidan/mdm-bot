<template>
  <div id="app">
    <div class="header">
      <h1>Каталог товаров</h1>
    </div>
    <ProductList />
  </div>
</template>

<script>
import ProductList from './components/ProductList.vue'

export default {
  name: 'App',
  components: {
    ProductList
  },
  mounted() {
    // Инициализация Telegram Web App
    if (window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp
      tg.ready()
      tg.expand()

      // Применяем тему Telegram
      document.body.style.backgroundColor = tg.themeParams.bg_color || '#ffffff'
    }
  }
}
</script>
