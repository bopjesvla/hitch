<template>
  <h2 class="ViewSpot__Header">
    <a v-if="link" target="_blank" :href="link">
      {{ title }}
    </a>
    <span v-else>{{ title }}</span>
  </h2>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

defineProps<{
  title: string;
  link?: string;
}>();
</script>

<style lang="scss" scoped>
.ViewSpot__Header {
  @apply text-center border-b-2 border-gray-200 pb-4 px-4 mb-4;

  span,
  a {
    @apply font-bold;
  }

  a {
    @apply border-none underline decoration-dotted !important;
  }
}
</style>
