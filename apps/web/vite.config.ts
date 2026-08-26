import { fileURLToPath, URL } from 'node:url'

import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],

  // One .env at the repository root feeds both applications. Only VITE_-prefixed
  // variables are exposed to the bundle, so API secrets in that file stay server-side.
  envDir: fileURLToPath(new URL('../../', import.meta.url)),

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },

  build: {
    target: 'es2022',
    sourcemap: true,
  },

  server: {
    port: 5173,
  },
})
