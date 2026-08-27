<script setup lang="ts">
import AppContainer from '@/components/base/AppContainer.vue'
import SectionHeading from '@/components/base/SectionHeading.vue'
</script>

<template>
  <AppContainer as="section" width="prose" class="py-20">
    <SectionHeading
      :level="1"
      eyebrow="Say hello"
      title="Contact"
      description="The accessible contact form, validation and rate-limit handling are built in T-208
        against the API from T-105."
    />
  </AppContainer>
</template>
