<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppHeader from '../components/AppHeader.vue'

const showModal = ref(false)

const toggleFAQ = (event: Event) => {
  const element = event.currentTarget as HTMLElement
  const allItems = document.querySelectorAll('.faq-item')

  // Close all other items
  allItems.forEach((item) => {
    if (item !== element) {
      item.classList.remove('active')
    }
  })

  // Toggle current item
  element.classList.toggle('active')

  // Haptic Feedback
  if (window.Telegram && window.Telegram.WebApp) {
    window.Telegram.WebApp.HapticFeedback.selectionChanged()
  }
}

const handleSupportSubmit = (event: Event) => {
  event.preventDefault()
  const form = event.target as HTMLFormElement
  const btn = form.querySelector('button') as HTMLButtonElement
  const originalText = btn.innerText

  // Loading state
  btn.disabled = true
  btn.innerText = 'ОТПРАВЛЯЕМ...'

  setTimeout(() => {
    btn.disabled = false
    btn.innerText = originalText
    form.reset()

    // Show modal
    showModal.value = true

    if (window.Telegram && window.Telegram.WebApp) {
      window.Telegram.WebApp.HapticFeedback.notificationOccurred('success')
    }
  }, 1200)
}

const closeModal = () => {
  showModal.value = false
}

onMounted(() => {
  // Initialize Telegram WebApp if available
  if (window.Telegram && window.Telegram.WebApp) {
    const tg = window.Telegram.WebApp
    tg.ready()
    tg.expand()
  }
})
</script>

<template>
  <div>
    <AppHeader title="помощь" back-link="/" />

    <main>
      <!-- Hero Section -->
      <section>
        <h2>
          есть вопросы? <br />
          <span>мы поможем.</span>
        </h2>
        <p>
          Найди ответ ниже или напиши нам напрямую — мы отвечаем в течение 15 минут.
        </p>
      </section>

      <!-- Status Indicator -->
      <section>
        <div>
          <span>
            <span></span>
            <span></span>
          </span>
          <span>сервис работает штатно</span>
        </div>
        <span>v.1.0.4</span>
      </section>

      <!-- FAQ Section -->
      <section>
        <h3>частые вопросы</h3>

        <div>
          <!-- FAQ Item 1 -->
          <div class="faq-item" @click="toggleFAQ">
            <div>
              <span>Как отследить мой заказ?</span>
              <div class="faq-icon">
                +
              </div>
            </div>
            <div class="faq-answer">
              <p>
                После оплаты бот пришлет вам трек-номер. Вы также можете найти его в разделе "Мои заказы" в главном меню.
              </p>
            </div>
          </div>

          <!-- FAQ Item 2 -->
          <div class="faq-item" @click="toggleFAQ">
            <div>
              <span>Какие сроки доставки?</span>
              <div class="faq-icon">
                +
              </div>
            </div>
            <div class="faq-answer">
              <p>
                Обычно доставка занимает от 3 до 7 рабочих дней в зависимости от вашего региона.
              </p>
            </div>
          </div>

          <!-- FAQ Item 3 -->
          <div class="faq-item" @click="toggleFAQ">
            <div>
              <span>Как сделать возврат?</span>
              <div class="faq-icon">
                +
              </div>
            </div>
            <div class="faq-answer">
              <p>
                Свяжитесь с поддержкой в течение 14 дней после получения товара. Товар должен сохранить товарный вид.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Quick Message Form -->
      <section>
        <h3>написать нам</h3>
        <form @submit="handleSupportSubmit">
          <div>
            <label>ваше сообщение</label>
            <textarea
              required
              placeholder="опишите проблему..."
              rows="3"
            ></textarea>
          </div>
          <button type="submit">
            отправить тикет
          </button>
        </form>
      </section>

      <!-- Direct Contact Grid -->
      <section>
        <a href="https://t.me/your_manager">
          <div>💬</div>
          <span>telegram</span>
        </a>
        <a href="mailto:support@mdm.com">
          <div>✉️</div>
          <span>email</span>
        </a>
      </section>
    </main>

    <!-- Success Modal -->
    <div v-if="showModal">
      <div>
        <div>🚀</div>
        <div>
          <h4>отправлено!</h4>
          <p>
            Менеджер свяжется с вами в ближайшее время.
          </p>
        </div>
        <button @click="closeModal">
          понятно
        </button>
      </div>
    </div>
  </div>
</template>
