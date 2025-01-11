<script setup lang="ts">
import Map from '@/components/Map/Map.vue';
import { onMounted, ref } from 'vue';
const hash = ref();

onMounted(() => {
  hash.value = window.location.hash;
});
</script>

<template>
  <a :href="`http://localhost:5173/beta/${hash}`">
    <Map noButtons />
  </a>
</template>
