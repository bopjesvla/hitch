<template>
  <div
    :class="`ViewSpot__Header ${$slots.default ? 'ViewSpot__Header--accordion' : ''}`"
    @click="expanded = !expanded"
  >
    <svg
      v-if="$slots.default"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 10 10"
      :class="`ViewSpot__HeaderAccordionToggle ${expanded ? 'rotate-90' : ''}`"
    >
      <polygon points="0,0 10,5 0,10" fill="black"></polygon>
    </svg>
    <h2>
      <a v-if="link" target="_blank" :href="link">
        {{ title }}
      </a>
      <span v-else>{{ title }}</span>
    </h2>
    <div class="ViewSpot__HeaderAccordion" v-if="$slots.default && expanded">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, ref } from 'vue';

defineProps<{
  title: string;
  link?: string;
}>();

const expanded = ref(false);
</script>

<style lang="scss" scoped>
.ViewSpot__Header {
  @apply relative text-center border-b-2 border-gray-200 pb-4 mb-4;

  span,
  a {
    @apply font-bold px-4;
  }

  a {
    @apply border-none underline decoration-dotted !important;
  }

  &--accordion {
    @apply cursor-pointer;
  }
}

.ViewSpot__HeaderAccordion {
  @apply mt-4;

  &Toggle {
    @apply size-3 absolute mt-1;
  }
}
</style>
