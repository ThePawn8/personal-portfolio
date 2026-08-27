<script setup lang="ts">
import { RouterLink } from 'vue-router'

import AppContainer from '@/components/base/AppContainer.vue'
import { navigation, site } from '@/config/site'

const year = new Date().getFullYear()
</script>

<template>
  <footer class="mt-24 border-t border-line py-10">
    <AppContainer>
      <div class="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex flex-col gap-1">
          <p class="font-medium text-fg">{{ site.name }}</p>
          <p class="text-sm text-fg-muted">{{ site.role }}</p>
        </div>

        <nav aria-label="Footer">
          <ul class="flex flex-wrap items-center gap-x-5 gap-y-2 text-sm">
            <li v-for="item in navigation" :key="item.routeName">
              <RouterLink
                :to="{ name: item.routeName }"
                class="rounded text-fg-muted transition-colors hover:text-fg"
              >
                {{ item.label }}
              </RouterLink>
            </li>
            <li>
              <a
                :href="site.githubUrl"
                class="rounded text-fg-muted transition-colors hover:text-fg"
                rel="noopener noreferrer"
                target="_blank"
              >
                GitHub
              </a>
            </li>
          </ul>
        </nav>
      </div>

      <p class="mt-8 text-xs text-fg-subtle">
        © {{ year }} {{ site.name }} ·
        <a
          :href="site.repositoryUrl"
          class="rounded underline underline-offset-4 hover:text-fg-muted"
          rel="noopener noreferrer"
          target="_blank"
        >
          Source on GitHub
        </a>
      </p>
    </AppContainer>
  </footer>
</template>
