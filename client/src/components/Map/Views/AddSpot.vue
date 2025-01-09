<template>
  <div v-if="currentComponent !== 'AddSpotForm'" class="AddSpot">
    <p v-if="!selectedCoords && !selectedPoint">
      Zoom the crosshairs into your hitchhiking spot. Be as precise as possible!
    </p>
    <p v-else>
      Where did your ride take you? Move the crosshairs near that location, then press done.
    </p>
    <div class="AddSpot__Actions">
      <button v-for="action in actions" @click="action.onClick" :key="action.label">
        {{ action.label }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import L from 'leaflet';

import { usePointsStore } from '@/stores/points';
import { useUiStore } from '@/stores/ui';

import Map from '../Leaflet';

const map = Map.getMap();

const pointsStore = usePointsStore();
const selectedPoint = computed(() => pointsStore.getSelectedPoint);

const uiStore = useUiStore();
const { selectedCoords, selectedDestCoords, currentComponent } = storeToRefs(uiStore);

onMounted(() => {
  if (!selectedPoint.value) return;
  const coords = new L.LatLng(selectedPoint.value.Latitude, selectedPoint.value.Longitude);
  map.setView(coords);
  uiStore.selectCoords(coords);
});

const skip = () => {
  uiStore.openSidebar('AddSpotForm');
};

const cancel = () => {
  uiStore.currentComponent = null;
  uiStore.currentMapAction = null;
  uiStore.resetCoords();
};

const actions = computed(() => {
  if (!selectedCoords.value && !selectedPoint.value) {
    return [
      { label: 'Done', onClick: () => uiStore.selectCoords(map.getCenter()) },
      { label: 'Cancel', onClick: cancel },
    ];
  }

  return [
    { label: 'Skip', onClick: skip },
    {
      label: 'Done',
      onClick: async () => {
        uiStore.selectDestCoords(map.getCenter());
        await uiStore.openSidebar('AddSpotForm');

        if (selectedCoords.value && selectedDestCoords.value) {
          const bounds = L.latLngBounds(selectedCoords.value, selectedDestCoords.value).pad(0.7);
          map.fitBounds(bounds, {
            paddingBottomRight: [
              document.querySelector('.Sidebar')?.getBoundingClientRect().width || 384,
              0,
            ],
          });
        }
      },
    },
    { label: 'Cancel', onClick: cancel },
  ];
});
</script>

<style lang="scss" scoped>
.AddSpot {
  @apply absolute flex flex-col items-center w-full bottom-6 z-50 text-black text-center block;

  &__Actions {
    @apply flex space-x-2;
  }

  p {
    @apply bg-white text-2xl;
  }

  &:before {
    content: '';
    pointer-events: none;
    position: fixed;
    left: 0px;
    top: 0px;
    right: 0px;
    bottom: 0px;
    margin: auto;
    width: 60vmin;
    height: 60vmin;
    background: linear-gradient(
        to right,
        transparent calc(50% - 1px),
        rgba(255, 0, 0, 0.5) calc(50% - 1px),
        rgba(255, 0, 0, 0.5) calc(50% + 1px),
        transparent calc(50% + 1px)
      ),
      linear-gradient(
        to bottom,
        transparent calc(50% - 1px),
        rgba(255, 0, 0, 0.5) calc(50% - 1px),
        rgba(255, 0, 0, 0.5) calc(50% + 1px),
        transparent calc(50% + 1px)
      );
  }
}
</style>
