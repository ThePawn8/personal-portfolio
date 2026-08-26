<script setup lang="ts">
/**
 * A short, non-interactive label: a technology, a tag, a project status.
 *
 * Deliberately not clickable. Filtering by tag happens through real controls on the
 * projects page (T-205); a badge that is sometimes a button and sometimes not is a
 * guessing game for anyone using a keyboard.
 */
type Tone = 'neutral' | 'accent' | 'outline'

withDefaults(defineProps<{ tone?: Tone }>(), { tone: 'neutral' })

const TONES: Record<Tone, string> = {
  neutral: 'bg-surface-raised text-fg-muted',
  accent: 'bg-accent/12 text-accent',
  outline: 'border border-line text-fg-muted',
}
</script>

<template>
  <span
    :class="[
      'inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium whitespace-nowrap',
      TONES[tone],
    ]"
  >
    <slot />
  </span>
</template>
