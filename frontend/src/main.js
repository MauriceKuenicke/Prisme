import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from '@/stores/auth'

function registerServiceWorker() {
  if (!('serviceWorker' in navigator) || !import.meta.env.PROD) {
    return
  }

  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch((error) => {
      console.error('Service worker registration failed:', error)
    })
  })
}

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

async function bootstrap() {
  const authStore = useAuthStore(pinia)
  await authStore.initializeAuth()

  app.use(router)
  app.mount('#app')
  registerServiceWorker()
}

bootstrap()
