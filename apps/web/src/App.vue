<script setup lang="ts">
/**
 * Design-system preview.
 *
 * A placeholder page that exercises every base component in one view, so the palette and
 * the components can be checked visually while they are still cheap to change. The router,
 * layout and navigation replace this in T-202.
 */
import AppContainer from '@/components/base/AppContainer.vue'
import BaseBadge from '@/components/base/BaseBadge.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseCard from '@/components/base/BaseCard.vue'
import SectionHeading from '@/components/base/SectionHeading.vue'

const tokens = [
  { name: 'canvas', class: 'bg-canvas' },
  { name: 'surface', class: 'bg-surface' },
  { name: 'surface-raised', class: 'bg-surface-raised' },
  { name: 'accent', class: 'bg-accent' },
  { name: 'danger', class: 'bg-danger' },
  { name: 'success', class: 'bg-success' },
]
</script>

<template>
  <main class="py-16">
    <AppContainer>
      <SectionHeading
        :level="1"
        size="display"
        eyebrow="T-201 · design system"
        title="Portfolio"
        description="Semantic tokens, two first-class themes, and the base components everything else is
          built from. Contrast is verified in both themes by npm run check:contrast."
      />

      <div class="mt-12 flex flex-col gap-12">
        <section class="flex flex-col gap-4">
          <h2 class="text-heading font-semibold">Buttons</h2>
          <div class="flex flex-wrap items-center gap-3">
            <BaseButton>Primary</BaseButton>
            <BaseButton variant="secondary">Secondary</BaseButton>
            <BaseButton variant="ghost">Ghost</BaseButton>
            <BaseButton size="sm">Small</BaseButton>
            <BaseButton loading>Sending</BaseButton>
            <BaseButton disabled>Disabled</BaseButton>
            <BaseButton href="https://github.com/ThePawn8/personal-portfolio">Link</BaseButton>
          </div>
        </section>

        <section class="flex flex-col gap-4">
          <h2 class="text-heading font-semibold">Badges</h2>
          <div class="flex flex-wrap gap-2">
            <BaseBadge>vue</BaseBadge>
            <BaseBadge tone="accent">featured</BaseBadge>
            <BaseBadge tone="outline">typescript</BaseBadge>
          </div>
        </section>

        <section class="flex flex-col gap-4">
          <h2 class="text-heading font-semibold">Surfaces</h2>
          <div class="grid gap-4 sm:grid-cols-2">
            <BaseCard>
              <h3 class="font-medium">Static card</h3>
              <p class="mt-2 text-sm text-fg-muted">
                Holds content. No hover state, because nothing here is clickable.
              </p>
            </BaseCard>
            <BaseCard interactive as="article">
              <h3 class="font-medium">
                <a class="text-accent underline-offset-4 hover:underline" href="#">Interactive</a>
              </h3>
              <p class="mt-2 text-sm text-fg-muted">
                The link inside takes focus; the card only reacts to it.
              </p>
            </BaseCard>
          </div>
        </section>

        <section class="flex flex-col gap-4">
          <h2 class="text-heading font-semibold">Palette</h2>
          <ul class="grid grid-cols-2 gap-3 sm:grid-cols-3">
            <li v-for="token in tokens" :key="token.name" class="flex items-center gap-3">
              <span :class="['size-10 rounded-control border border-line', token.class]" />
              <code class="font-mono text-xs text-fg-muted">{{ token.name }}</code>
            </li>
          </ul>
        </section>
      </div>
    </AppContainer>
  </main>
</template>
