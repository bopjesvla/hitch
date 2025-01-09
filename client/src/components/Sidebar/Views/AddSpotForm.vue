<template>
  <div>
    <SidebarHeader :title="selectedPoint ? `New Review` : `New Spot`" />
    <form class="space-y-4" @submit.prevent="submitForm">
      <span class="block font-sm text-center bg-slate-100">{{
        `${[Number(lat).toFixed(4), Number(lon).toFixed(4)].join(', ')} &#8594; ${
          destLat && destLon
            ? [destLat.toFixed(4), destLon.toFixed(4)].join(', ')
            : 'unknown destination'
        }`
      }}</span>
      <div class="AddSpotForm__InputGroup">
        <b>How do you rate the spot?</b>
        <div class="flex flex-row-reverse justify-end">
          <template v-for="x in [...Array(5).keys()]" :key="`STAR:${x}`">
            <input
              v-model="rating"
              type="radio"
              :id="`st-${x}`"
              :value="5 - x"
              name="star-radio"
              class="peer hidden"
              :disabled="isSubmitting"
            />
            <label
              :for="`st-${x}`"
              class="text-3xl text-slate-300 peer-hover:text-yellow-500 peer-checked:text-yellow-400"
              >★</label
            >
          </template>
        </div>
      </div>
      <div class="AddSpotForm__InputGroup">
        <b>How long did you wait?</b>
        <span class="AddSpotForm__Hint block">Leave blank if you don't remember.</span>
        <div class="flex items-end">
          <input
            v-model="duration"
            type="number"
            class="border-r-0 text-right"
            :disabled="isSubmitting"
          />
          <span class="border border-l-0 p-2">minutes</span>
        </div>
      </div>
      <div class="AddSpotForm__InputGroup">
        <b>Comment <span class="AddSpotForm__Hint">(optional)</span></b>
        <textarea v-model="comment" :disabled="isSubmitting" />
      </div>
      <div class="AddSpotForm__InputGroup">
        <b>Public nickname <span class="AddSpotForm__Hint">(alphanumeric)</span></b>
        <input v-model="name" type="text" :disabled="isSubmitting" />
      </div>
      <button type="submit" :disabled="isSubmitting">
        {{ isSubmitting ? `Submitting...` : `Submit` }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useUiStore } from '@/stores/ui';
import { usePointsStore } from '@/stores/points';

import SidebarHeader from '../SidebarHeader.vue';

const uiStore = useUiStore();
const pointsStore = usePointsStore();

const { selectedCoords, selectedDestCoords } = storeToRefs(uiStore);
const selectedPoint = computed(() => pointsStore.getSelectedPoint);
const isSubmitting = computed(() => pointsStore.isSubmitting);

const lat = computed(() => selectedPoint.value?.Latitude || selectedCoords.value?.lat || '');
const lon = computed(() => selectedPoint.value?.Longitude || selectedCoords.value?.lng || '');
const destLat = selectedDestCoords.value?.lat || '';
const destLon = selectedDestCoords.value?.lng || '';

// Form
const rating = ref();
const duration = ref();
const comment = ref();
const name = ref();

const submitForm = async () => {
  if (!lat.value || !lon.value || !rating.value) return;

  const reviewInput = {
    Rating: rating.value,
    Duration: duration.value,
    Comment: comment.value,
    Name: name.value,
  };

  if (selectedPoint.value) {
    await pointsStore.createReview({
      PointId: selectedPoint.value.ID,
      ...reviewInput,
    });
  } else {
    const point = await pointsStore.createPoint({
      Latitude: lat.value,
      Longitude: lon.value,
      Review: reviewInput,
    });

    if (point) pointsStore.selectPoint(point);
  }

  uiStore.resetCoords();
  return uiStore.openSidebar('ViewSpot');
};
</script>

<style lang="scss" scoped>
.AddSpotForm {
  &__Hint {
    @apply text-xs opacity-75;
  }

  &__InputGroup {
    textarea,
    input {
      @apply mt-2;
    }
  }
}
</style>
