<script setup lang="ts">
/**
 * Placeholder shell. The real layout, router and navigation arrive in T-202,
 * on top of the design system from T-201.
 */
const buildStage = 'T-002 · scaffold'
</script>

<template>
  <main class="grid min-h-dvh place-items-center bg-neutral-950 px-6 text-neutral-100">
    <div class="max-w-md text-center">
      <p class="mb-3 font-mono text-xs tracking-widest text-teal-400 uppercase">
        {{ buildStage }}
      </p>
      <h1 class="mb-4 text-3xl font-semibold text-balance">Portfolio</h1>
      <p class="text-sm leading-relaxed text-neutral-400 text-pretty">
        Toolchain is wired: Vue 3, TypeScript strict, Tailwind v4, Vitest and Playwright. The
        application itself is built ticket by ticket.
      </p>
    </div>
  </main>
</template>
