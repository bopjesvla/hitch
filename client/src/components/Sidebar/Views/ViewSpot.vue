<template>
  <div v-if="point">
    <SidebarHeader
      :title="`${point.Latitude.toFixed(8)}, ${point.Longitude.toFixed(8)}`"
      :link="`https://www.google.com/maps/place/${point.Latitude},${point.Longitude}`"
    />
    <p>
      Rating: {{ point.Rating }}/5<br />
      Waiting time: {{ point.Duration ? `${point.Duration} min` : '-' }}<br />
      Ride distance: -
      <!-- TODO: Avg Distance -->
    </p>
    <div v-if="reviewsWithComments?.length !== 0">
      <h3>Comments</h3>
      <div class="divide-y">
        <div class="py-4" v-for="Review in reviewsWithComments" :key="Review.ID">
          <p class="mb-4">{{ Review.Comment }}</p>
          <span class="text-xs text-right w-full block text-opacity-50">
            {{
              [
                Review.Rating ? `Rating: ${Review.Rating}/5` : null,
                Review.Duration ? `Wait: ${Review.Duration}min` : null,
              ]
                .filter((n) => n)
                .join(', ')
            }}
          </span>
          <span class="text-xs text-right w-full block text-opacity-50"
            >–
            {{
              [
                Review.Name || 'Anonymous',
                Review.CreatedAt
                  ? new Intl.DateTimeFormat('en-US', {
                      month: 'long',
                      year: 'numeric',
                    }).format(new Date(Review.CreatedAt))
                  : null,
              ]
                .filter((n) => n)
                .join(', ')
            }}</span
          >
        </div>
      </div>
    </div>
    <button @click="handleAddReview">Review Spot</button>
  </div>
</template>

<script setup lang="ts">
import { useUiStore } from '@/stores/ui';
import { usePointsStore } from '@/stores/points';
import { computed } from 'vue';

import SidebarHeader from '../SidebarHeader.vue';

const uiStore = useUiStore();
const pointsStore = usePointsStore();

const point = computed(() => pointsStore.getSelectedPoint);
const reviewsWithComments = computed(() =>
  point.value?.Reviews.filter((r) => !!r.Comment).sort(
    (a, b) => new Date(b.CreatedAt).valueOf() - new Date(a.CreatedAt).valueOf(),
  ),
);

const handleAddReview = () => {
  uiStore.closeSidebar();
  uiStore.currentMapAction = 'AddSpot';
};
</script>

<style lang="scss" scoped>
.ViewSpot__Header {
  @apply font-bold text-center border-b-2 border-gray-200 pb-4 px-4 mb-4;

  a {
    @apply border-none underline decoration-dotted !important;
  }
}
</style>
