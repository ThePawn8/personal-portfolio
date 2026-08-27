<script setup lang="ts">
import AppContainer from '@/components/base/AppContainer.vue'
import SectionHeading from '@/components/base/SectionHeading.vue'
</script>

<template>
  <AppContainer as="section" width="prose" class="py-20">
    <SectionHeading
      :level="1"
      eyebrow="Background"
      title="About"
      description="Bio, experience timeline, education and skills are built in T-207 from the profile
        content authored in T-302."
    />
  </AppContainer>
</template>
