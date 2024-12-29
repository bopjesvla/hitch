<template>
  <component v-if="currentMapAction" :is="MapActionComponents[currentMapAction]" />
  <div id="map"></div>
</template>

<script setup lang="ts">
import { onMounted, type Component } from 'vue';
import L from 'leaflet';
import Map from './Leaflet.ts';

import AddSpotButton from './Controls/AddSpotButton';
import MenuButton from './Controls/MenuButton';
// import RouteButton from './Controls/RouteButton';

import AddSpot from './Views/AddSpot.vue';

// Stores
import { usePointsStore } from '@/stores/points';
import { COLOR_BY_RATING, OPACITY_BY_RATING } from './MapConstants';
import { useUiStore } from '@/stores/ui';
import { storeToRefs } from 'pinia';

const pointsStore = usePointsStore();
const uiStore = useUiStore();

const { currentMapAction } = storeToRefs(uiStore);

const MapActionComponents: { [key: string]: Component } = {
  AddSpot,
};

onMounted(async () => {
  const map = Map.getMap();

  // Initialize Controls
  L.control.scale().addTo(map);

  new MenuButton().addTo(map);
  new AddSpotButton().addTo(map);
  // new RouteButton().addTo(map);
  // new RouteViewButton().addTo(map);
  // new CancelRouteButton().addTo(map);
  L.control.zoom().addTo(map);

  // Initialize Tile Layer
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(map);

  // Fetch points and put them on the map!
  await pointsStore.fetchPoints();

  const markers = (L as any).markerClusterGroup({
    bubblingMouseEvents: false,
    spiderfyOnMaxZoom: false,
    disableClusteringAtZoom: 7, // Any higher and it crashes early
  });

  pointsStore.items.map((point) => {
    const marker = L.circleMarker(L.latLng(point.lat, point.lon), {
      radius: 5,
      weight: point.reviewCount ? 1 + (point.reviewCount > 2 ? 1 : 0) : 1,
      color: 'black',
      fillOpacity: OPACITY_BY_RATING[point.rating as keyof typeof OPACITY_BY_RATING],
      fillColor: COLOR_BY_RATING[point.rating as keyof typeof COLOR_BY_RATING],
    });

    marker.on('click', () => {
      pointsStore.selectPoint(point);
      uiStore.openSidebar('ViewSpot');
    });

    markers.addLayer(marker);
  });

  map.addLayer(markers);

  // TODO: Center on Coords if available
  // if (!window.location.hash.includes(',')) {
  //   map.fitBounds;
  // }
});
</script>

<style scoped>
#map {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
</style>
