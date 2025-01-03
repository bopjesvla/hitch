<template>
  <div v-if="currentComponent !== 'AddSpotForm'" class="AddSpot">
    <p v-if="!selectedCoords">
      Zoom the crosshairs into your hitchhiking spot. Be as precise as possible!
    </p>
    <p v-else>
      Where did your ride take you? Move the crosshairs near that location, then press done.
    </p>
    <div class="AddSpot__Actions">
      <button v-for="action in actions" @click="action.onClick" :key="action.label">{{ action.label }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUiStore } from '@/stores/ui';
import { computed } from 'vue';
import Map from '../Leaflet';
import { storeToRefs } from 'pinia';

const map = Map.getMap();

const uiStore = useUiStore();
const { selectedCoords, selectedDestCoords, currentComponent } = storeToRefs(uiStore);

const selectCoords = () => {
  selectedCoords.value = map.getCenter();

  // TODO: Add Marker to Map
  // TODO: Set Opacity of other Markers to 0.5
};

const selectDestCoords = () => {
  selectedDestCoords.value = map.getCenter();
  uiStore.openSidebar('AddSpotForm');
};

const skip = () => {
  uiStore.openSidebar('AddSpotForm');
};

const cancel = () => {
  uiStore.currentComponent = null;
  uiStore.currentMapAction = null;
};

const actions = computed(() => {
  if (!selectedCoords.value) {
    return [
      { label: 'Done', onClick: selectCoords },
      { label: 'Cancel', onClick: cancel },
    ];
  }

  return [
    { label: 'Skip', onClick: skip },
    { label: 'Done', onClick: selectDestCoords },
    { label: 'Cancel', onClick: cancel },
  ];
});
</script>

<style lang="scss" scoped>
.AddSpot {
  @apply absolute flex flex-col items-center w-full bottom-6 z-50 text-black text-center block;

  &__Actions {
    @apply space-x-2;
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
