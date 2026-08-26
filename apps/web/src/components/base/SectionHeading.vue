<script setup lang="ts">
/**
 * The heading block that opens every section.
 *
 * `level` is a prop rather than a fixed `h2` because heading level is document structure,
 * not decoration: a screen reader user navigates by it. Size comes from the type scale, so
 * a correctly nested `h3` can still look large where the design calls for it.
 *
 * Use `level="1"` exactly once per page, for the page title.
 */
withDefaults(
  defineProps<{
    title: string
    /** Small label above the title. Decorative — never the only source of meaning. */
    eyebrow?: string
    description?: string
    level?: 1 | 2 | 3
    size?: 'display' | 'title' | 'heading'
  }>(),
  // `eyebrow` and `description` are intentionally absent rather than defaulted to
  // `undefined`: `exactOptionalPropertyTypes` distinguishes the two.
  { level: 2, size: 'title' },
)

const SIZES = {
  display: 'text-display font-semibold',
  title: 'text-title font-semibold',
  heading: 'text-heading font-semibold',
} as const
</script>

<template>
  <div class="flex flex-col gap-3">
    <p v-if="eyebrow" class="text-eyebrow font-medium text-accent uppercase">
      {{ eyebrow }}
    </p>

    <component :is="`h${level}`" :class="['text-fg text-balance', SIZES[size]]">
      {{ title }}
    </component>

    <p v-if="description" class="max-w-2xl text-fg-muted text-pretty">
      {{ description }}
    </p>
  </div>
</template>
