<script setup lang="ts">
/**
 * Horizontal rhythm for the whole site: one max width, one gutter, defined once.
 *
 * Without this, page width drifts section by section and the layout stops feeling
 * deliberate — the most common tell of a hand-assembled portfolio.
 */
withDefaults(
  defineProps<{
    /** Element to render. Sections and articles carry more meaning than a div. */
    as?: string
    /** `prose` narrows to a comfortable measure (~68 characters) for long-form text. */
    width?: 'default' | 'prose' | 'wide'
  }>(),
  { as: 'div', width: 'default' },
)

const WIDTHS = {
  default: 'max-w-5xl',
  prose: 'max-w-2xl',
  wide: 'max-w-7xl',
} as const
</script>

<template>
  <component :is="as" :class="['mx-auto w-full px-5 sm:px-8', WIDTHS[width]]">
    <slot />
  </component>
</template>
