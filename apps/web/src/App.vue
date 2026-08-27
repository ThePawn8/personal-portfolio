<script setup lang="ts">
import { RouterView } from 'vue-router'

import AppFooter from '@/components/layout/AppFooter.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
</script>

<template>
  <!-- First focusable element on the page: a keyboard user can jump past the navigation
       instead of tabbing through it on every route. -->
  <a class="skip-link" href="#main-content">Skip to content</a>

  <div class="flex min-h-dvh flex-col">
    <AppHeader />

    <main id="main-content" class="flex-1" tabindex="-1">
      <RouterView v-slot="{ Component }">
        <component :is="Component" />
      </RouterView>
    </main>

    <AppFooter />
  </div>
</template>
