<script setup lang="ts">
import AppContainer from '@/components/base/AppContainer.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import SectionHeading from '@/components/base/SectionHeading.vue'
</script>

<template>
  <AppContainer as="section" width="prose" class="py-24">
    <SectionHeading
      :level="1"
      size="display"
      eyebrow="404"
      title="Page not found"
      description="That address does not match anything here. It may have moved, or never existed."
    />

    <div class="mt-8">
      <BaseButton :to="{ name: 'home' }">Back to home</BaseButton>
    </div>
  </AppContainer>
</template>
