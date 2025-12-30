<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps<{
  title?: string
  backLink?: string
  showStatus?: boolean
  showCart?: boolean
  cartCount?: number
}>()

const route = useRoute()

const displayTitle = computed(() => props.title || 'mdm bot')
const showBackButton = computed(() => !!props.backLink)
</script>

<template>
  <header>
    <nav>
      <div v-if="showBackButton">
        <router-link :to="backLink!">
          <div>
            ←
          </div>
          <h1>{{ displayTitle }}</h1>
        </router-link>
      </div>

      <div v-else>
        <div>
          m
        </div>
        <h1>{{ displayTitle }}</h1>
      </div>

      <!-- API Status -->
      <div v-if="showStatus" id="api-status">
        <span></span>
        ONLINE
      </div>

      <!-- Cart Counter -->
      <div v-else-if="showCart">
        {{ cartCount || 0 }} ТОВАРОВ
      </div>

      <!-- Help Icon (for support page) -->
      <div v-else-if="route.path === '/support'">
        ?
      </div>
    </nav>
  </header>
</template>
