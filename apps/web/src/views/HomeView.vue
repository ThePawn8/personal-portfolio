<script setup lang="ts">
import AppContainer from '@/components/base/AppContainer.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import SectionHeading from '@/components/base/SectionHeading.vue'
import { site } from '@/config/site'
</script>

<template>
  <AppContainer as="section" class="py-20">
    <SectionHeading
      :level="1"
      size="display"
      :eyebrow="site.role"
      :title="site.name"
      description="Placeholder hero. The real content, featured projects and skills summary arrive in
        T-204, once the API and the case studies exist."
    />

    <div class="mt-8 flex flex-wrap gap-3">
      <BaseButton :to="{ name: 'projects' }">View work</BaseButton>
      <BaseButton variant="secondary" :to="{ name: 'contact' }">Get in touch</BaseButton>
    </div>
  </AppContainer>
</template>
