<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, RouterLink } from 'vue-router'

import AppContainer from '@/components/base/AppContainer.vue'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import { navigation, site } from '@/config/site'

const route = useRoute()
const isMenuOpen = ref(false)

// Leaving the menu open across a navigation hides the page the visitor just asked for.
watch(
  () => route.fullPath,
  () => {
    isMenuOpen.value = false
  },
)
</script>

<template>
  <header
    class="sticky top-0 z-50 border-b border-line bg-canvas/85 backdrop-blur-md"
    @keydown.escape="isMenuOpen = false"
  >
    <AppContainer>
      <div class="flex h-16 items-center justify-between gap-4">
        <RouterLink
          :to="{ name: 'home' }"
          class="rounded-control font-semibold tracking-tight text-fg"
        >
          {{ site.name }}
        </RouterLink>

        <div class="flex items-center gap-2">
          <nav aria-label="Main" class="hidden sm:block">
            <ul class="flex items-center gap-1">
              <li v-for="item in navigation" :key="item.routeName">
                <RouterLink
                  :to="{ name: item.routeName }"
                  class="rounded-control px-3 py-2 text-sm text-fg-muted transition-colors hover:bg-surface-raised hover:text-fg"
                  active-class="text-fg"
                  :aria-current="route.name === item.routeName ? 'page' : undefined"
                >
                  {{ item.label }}
                </RouterLink>
              </li>
            </ul>
          </nav>

          <ThemeToggle />

          <button
            type="button"
            class="rounded-control p-2 text-fg-muted transition-colors hover:bg-surface-raised hover:text-fg sm:hidden"
            :aria-expanded="isMenuOpen"
            aria-controls="mobile-navigation"
            @click="isMenuOpen = !isMenuOpen"
          >
            <span class="sr-only">{{ isMenuOpen ? 'Close menu' : 'Open menu' }}</span>
            <svg
              class="size-5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              aria-hidden="true"
            >
              <path v-if="isMenuOpen" d="M6 6l12 12M18 6L6 18" />
              <path v-else d="M4 7h16M4 12h16M4 17h16" />
            </svg>
          </button>
        </div>
      </div>

      <nav v-if="isMenuOpen" id="mobile-navigation" aria-label="Main" class="pb-4 sm:hidden">
        <ul class="flex flex-col gap-1">
          <li v-for="item in navigation" :key="item.routeName">
            <RouterLink
              :to="{ name: item.routeName }"
              class="block rounded-control px-3 py-2.5 text-fg-muted transition-colors hover:bg-surface-raised hover:text-fg"
              active-class="text-fg"
              :aria-current="route.name === item.routeName ? 'page' : undefined"
            >
              {{ item.label }}
            </RouterLink>
          </li>
        </ul>
      </nav>
    </AppContainer>
  </header>
</template>
