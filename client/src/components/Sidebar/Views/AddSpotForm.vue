<template>
  <div>
    <form @submit.prevent="submitForm">
      <p>Latitude: {{ lat }}</p>
      <p>Longitude: {{ lon }}</p>
      <p v-if="destLat">Destination Latitude: {{ destLat }}</p>
      <p v-if="destLon">Destination Longitude: {{ destLon }}</p>
      <input type="submit" value="Add Spot" />
    </form>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useUiStore } from '@/stores/ui';
import { usePointsStore } from '@/stores/points';

const uiStore = useUiStore();
const pointsStore = usePointsStore();

const { selectedCoords, selectedDestCoords } = storeToRefs(uiStore);

const lat = selectedCoords.value?.lat || '';
const lon = selectedCoords.value?.lng || '';
const destLat = selectedDestCoords.value?.lat || '';
const destLon = selectedDestCoords.value?.lng || '';

const submitForm = () => {
  if (lat && lon) {
    const newPoint = {
      id: Date.now(),
      lat,
      lon,
      // Add other properties if needed
    };

    pointsStore.createPoint(newPoint);
  }
};
</script>
