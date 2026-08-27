<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, type RouteLocationRaw } from 'vue-router'

/**
 * The one interactive control in the system.
 *
 * Renders a `<button>`, an `<a>` when given `href`, or a `RouterLink` when given `to` —
 * because a control that navigates must be a link (middle-click, open in new tab and copy
 * address all have to work) and a control that acts must be a button. Styling one to look
 * like the other is where keyboard and screen reader support usually breaks.
 */
type Variant = 'primary' | 'secondary' | 'ghost'
type Size = 'sm' | 'md'

const props = withDefaults(
  defineProps<{
    variant?: Variant
    size?: Size
    /** Internal navigation -> renders a RouterLink (a real anchor, client-side routed). */
    to?: RouteLocationRaw
    /** External navigation -> renders a plain anchor. */
    href?: string
    /** Only meaningful for buttons. */
    type?: 'button' | 'submit'
    disabled?: boolean
    /** Shows a spinner, blocks interaction and announces the busy state. */
    loading?: boolean
  }>(),
  // Optional props are left out entirely rather than defaulted to `undefined`:
  // `exactOptionalPropertyTypes` treats "absent" and "explicitly undefined" as different.
  { variant: 'primary', size: 'md', type: 'button', disabled: false, loading: false },
)

const VARIANTS: Record<Variant, string> = {
  primary: 'bg-accent text-on-accent hover:bg-accent-hover',
  secondary: 'bg-surface text-fg border border-line-strong hover:bg-surface-raised',
  ghost: 'text-fg-muted hover:text-fg hover:bg-surface-raised',
}

const SIZES: Record<Size, string> = {
  sm: 'h-9 px-3.5 text-sm gap-1.5',
  md: 'h-11 px-5 text-base gap-2',
}

const element = computed(() => {
  if (props.to !== undefined) return RouterLink
  return props.href !== undefined ? 'a' : 'button'
})

/** Loading is a form of disabled — otherwise a double submit is one impatient click away. */
const isInactive = computed(() => props.disabled || props.loading)

/**
 * Attributes are composed per element rather than bound individually.
 *
 * Binding `:href="undefined"` alongside `:to` looks harmless but is not: the undefined
 * attribute falls through onto the anchor RouterLink renders and overrides the href it
 * computed, producing an `<a>` with no href — which has no link role, is unreachable by
 * keyboard and is invisible to assistive technology.
 */
const elementAttrs = computed(() => {
  if (props.to !== undefined) {
    return { to: props.to, 'aria-disabled': isInactive.value ? 'true' : undefined }
  }

  if (props.href !== undefined) {
    return { href: props.href, 'aria-disabled': isInactive.value ? 'true' : undefined }
  }

  return { type: props.type, disabled: isInactive.value }
})
</script>

<template>
  <component
    :is="element"
    :class="[
      'inline-flex items-center justify-center rounded-control font-medium',
      'transition-colors duration-150',
      'disabled:pointer-events-none disabled:opacity-50 aria-disabled:opacity-50',
      VARIANTS[variant],
      SIZES[size],
    ]"
    v-bind="elementAttrs"
    :aria-busy="loading ? 'true' : undefined"
  >
    <svg
      v-if="loading"
      class="size-4 animate-spin"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" opacity="0.25" />
      <path d="M22 12a10 10 0 0 1-10 10" stroke="currentColor" stroke-width="3" />
    </svg>
    <slot />
  </component>
</template>
