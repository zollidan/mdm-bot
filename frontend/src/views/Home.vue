<script setup lang="ts">
import { ref, onMounted } from "vue";
import AppHeader from "../components/AppHeader.vue";

interface Product {
  id: number;
  name: string;
  price: number;
  vendor_code?: string;
  image?: string;
}

interface ApiResponse {
  items: Product[];
}

const featuredProducts = ref<Product[]>([]);
const isLoading = ref(true);
const hasError = ref(false);
const apiOnline = ref(true);

const fetchFeaturedProducts = async () => {
  try {
    const response = await fetch("/api/products?limit=3");
    const data: ApiResponse = await response.json();

    if (data.items && data.items.length > 0) {
      featuredProducts.value = data.items;
    }
    isLoading.value = false;
  } catch (error) {
    console.error("Ошибка загрузки:", error);
    hasError.value = true;
    apiOnline.value = false;
    isLoading.value = false;
  }
};

const checkHealth = async () => {
  try {
    const res = await fetch("/api/health");
    if (!res.ok) throw new Error();
  } catch {
    apiOnline.value = false;
  }
};

onMounted(() => {
  fetchFeaturedProducts();
  checkHealth();
});
</script>

<template>
  <div>
    <AppHeader :show-status="true" />

    <main>
      <!-- Hero Section -->
      <section>
        <h2>
          твой новый уровень шоппинга
        </h2>
        <p>
          Лучшие товары прямо внутри твоего Telegram. Быстро, стильно, надежно.
        </p>
        <router-link to="/products">
          открыть каталог ↗
        </router-link>
      </section>

      <!-- Stats Grid -->
      <section>
        <div>
          <p>
            доставка
          </p>
          <p>24/7</p>
        </div>
        <div>
          <p>
            поддержка
          </p>
          <p>LIVE</p>
        </div>
      </section>

      <!-- Featured Products -->
      <section>
        <div>
          <h3>новинки</h3>
          <router-link to="/products">
            смотреть все
          </router-link>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading">
          <div>
            <span>Загружаем стильные вещи...</span>
          </div>
        </div>

        <!-- Error State -->
        <div v-else-if="hasError">
          <div>
            <p>
              Ошибка связи с базой. Проверь интернет!
            </p>
          </div>
        </div>

        <!-- Products Grid -->
        <div v-else>
          <div v-for="product in featuredProducts" :key="product.id">
            <div>
              <img
                v-if="product.image"
                :src="product.image"
                :alt="product.name"
              />
              <span v-else>📦</span>
            </div>
            <div>
              <div>
                <p>
                  art: {{ product.vendor_code || "N/A" }}
                </p>
                <h4>
                  {{ product.name }}
                </h4>
              </div>
              <div>
                <span>{{ product.price.toLocaleString() }} ₽</span>
                <router-link :to="`/products/${product.id}`">
                  →
                </router-link>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-if="featuredProducts.length === 0">
            <p>
              Склад пуст, но скоро здесь будет жарко 🔥
            </p>
          </div>
        </div>
      </section>

      <!-- Footer / Contact -->
      <footer>
        <div>
          <p>
            остались вопросы?
          </p>
          <p>
            Напиши нашему менеджеру в одно касание. Мы всегда на связи.
          </p>
        </div>
        <router-link to="/support">
          написать в поддержку
        </router-link>
        <div>
          v1.0.0 — mdm digital systems
        </div>
      </footer>
    </main>
  </div>
</template>
