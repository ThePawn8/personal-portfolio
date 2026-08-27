<script setup lang="ts">
import { useTheme, type Theme } from '@/composables/useTheme'

/**
 * Native radio inputs rather than buttons with `role="radio"`.
 *
 * Radios in a fieldset give arrow-key navigation, group semantics and the selected state
 * to assistive technology for free. Rebuilding that with ARIA is more code that works less
 * well.
 */
const { theme, setTheme } = useTheme()

const OPTIONS: { value: Theme; label: string }[] = [
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
  { value: 'system', label: 'System' },
]
</script>

<template>
  <fieldset class="flex items-center gap-0.5 rounded-full border border-line p-0.5">
    <legend class="sr-only">Colour theme</legend>

    <label
      v-for="option in OPTIONS"
      :key="option.value"
      :class="[
        'cursor-pointer rounded-full p-1.5 transition-colors',
        'has-[:focus-visible]:outline has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-ring',
        theme === option.value ? 'bg-surface-raised text-fg' : 'text-fg-subtle hover:text-fg-muted',
      ]"
      :title="option.label"
    >
      <input
        class="sr-only"
        type="radio"
        name="theme"
        :value="option.value"
        :checked="theme === option.value"
        @change="setTheme(option.value)"
      />
      <span class="sr-only">{{ option.label }}</span>

      <svg
        class="size-4"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <template v-if="option.value === 'light'">
          <circle cx="12" cy="12" r="4" />
          <path
            d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"
          />
        </template>
        <template v-else-if="option.value === 'dark'">
          <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z" />
        </template>
        <template v-else>
          <rect x="2" y="4" width="20" height="14" rx="2" />
          <path d="M8 21h8M12 18v3" />
        </template>
      </svg>
    </label>
  </fieldset>
</template>
