<script setup lang="ts">
import AppContainer from '@/components/base/AppContainer.vue'
import SectionHeading from '@/components/base/SectionHeading.vue'
</script>

<template>
  <AppContainer as="section" class="py-20">
    <SectionHeading
      :level="1"
      eyebrow="Selected work"
      title="Work"
      description="The project grid, tag filtering and card states are built in T-205, on top of the
        typed API client from T-203."
    />
  </AppContainer>
</template>
