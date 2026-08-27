<script setup lang="ts">
import AppContainer from '@/components/base/AppContainer.vue'
import SectionHeading from '@/components/base/SectionHeading.vue'

defineProps<{ slug: string }>()
</script>

<template>
  <AppContainer as="article" width="prose" class="py-20">
    <SectionHeading
      :level="1"
      eyebrow="Case study"
      :title="slug"
      description="The case-study layout, mockup gallery and impact metrics are built in T-206."
    />
  </AppContainer>
</template>
