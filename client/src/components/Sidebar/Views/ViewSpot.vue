<template>
  <div v-if="point">
    <h2 class="ViewSpot__Header">
      <a target="_blank" :href="`https://www.google.com/maps/place/${point.Latitude},${point.Longitude}`">
        <!-- TODO: Shorten the strings, add link icon -->
        {{ point.Latitude }}, {{ point.Longitude }}
      </a>
    </h2>
    <p>
      Rating: {{ point.rating }}/5<br>
      Waiting time: {{ point.wait ? `${point.wait} min` : '-' }}<br>
      Ride distance: - <!-- TODO -->
    </p>
    <h3>Comments</h3>
  </div>
</template>

<script setup lang="ts">
import { usePointsStore } from '@/stores/points';
import { computed } from 'vue';

const pointsStore = usePointsStore();
const point = computed(() => pointsStore.getSelectedPoint);
</script>

<style lang="scss" scoped>
.ViewSpot__Header {
  @apply font-bold text-center border-b-2 border-gray-200 pb-4 mb-4;

  a {
    @apply border-b-black border-dotted;
  }
}
</style>
