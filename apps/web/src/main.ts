import { createHead } from '@unhead/vue/client'
import { createApp } from 'vue'

import App from './App.vue'
import { router } from './router'
import './assets/main.css'

const app = createApp(App)

/**
 * Errors that escape a component would otherwise vanish into the console with no context.
 * Sentry is deliberately out of scope (ARCHITECTURE § 10); this at least makes the failure
 * legible while developing and keeps one place to send them from later.
 */
app.config.errorHandler = (error, _instance, info) => {
  console.error('[app] unhandled error', { error, info })
}

app.use(router)
app.use(createHead())

app.mount('#app')
