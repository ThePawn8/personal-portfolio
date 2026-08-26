<script setup lang="ts">
/**
 * A raised surface: project cards, metric tiles, message panels.
 *
 * `interactive` styles the card as a hover/focus target but adds no click handler and no
 * tabindex. The card is a container; the link inside it is what receives focus. Making the
 * whole card focusable would duplicate every card in the tab order.
 */
withDefaults(
  defineProps<{
    as?: string
    interactive?: boolean
    padding?: 'none' | 'sm' | 'md'
  }>(),
  { as: 'div', interactive: false, padding: 'md' },
)

const PADDING = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
} as const
</script>

<template>
  <component
    :is="as"
    :class="[
      'rounded-card border border-line bg-surface',
      PADDING[padding],
      interactive &&
        'transition-colors duration-150 hover:border-line-strong hover:bg-surface-raised focus-within:border-line-strong',
    ]"
  >
    <slot />
  </component>
</template>
