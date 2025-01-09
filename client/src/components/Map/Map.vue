<template>
  <component v-if="currentMapAction" :is="MapActionComponents[currentMapAction]" />
  <div id="map"></div>
</template>

<script setup lang="ts">
import { onMounted, type Component, computed, shallowRef } from 'vue';
import L from 'leaflet';
import Map from './Leaflet.ts';

import AddSpotButton from './Controls/AddSpotButton';
import MenuButton from './Controls/MenuButton';
// import RouteButton from './Controls/RouteButton';

import AddSpot from './Views/AddSpot.vue';

// Stores
import { usePointsStore, type Point } from '@/stores/points';
import { COLOR_BY_RATING, OPACITY_BY_RATING } from './MapConstants';
import { useUiStore } from '@/stores/ui';
import { storeToRefs } from 'pinia';

const pointsStore = usePointsStore();
const uiStore = useUiStore();

const { currentMapAction } = storeToRefs(uiStore);
const points = computed(() => pointsStore.items);

const originMarker = shallowRef<L.Marker>();
const destMarker = shallowRef<L.Marker>();

const MapActionComponents: { [key: string]: Component } = {
  AddSpot,
};

const targetMarker = (point: L.LatLng) => L.marker(point);

const circleMarker = (point: Point) =>
  L.circleMarker(L.latLng(point.Latitude, point.Longitude), {
    radius: 5,
    weight: point.ReviewCount ? 1 + (point.ReviewCount > 2 ? 1 : 0) : 1,
    color: 'black',
    fillOpacity: OPACITY_BY_RATING[point.Rating as keyof typeof OPACITY_BY_RATING],
    fillColor: COLOR_BY_RATING[point.Rating as keyof typeof COLOR_BY_RATING],
  });

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

  points.value.map((point) => {
    const marker = circleMarker(point);

    marker.on('click', () => {
      pointsStore.selectPoint(point);
      uiStore.openSidebar('ViewSpot');
    });

    markers.addLayer(marker);
  });

  map.addLayer(markers);

  // Listen for points being added and add them to the map immediately
  pointsStore.$onAction(({ name, after }) => {
    if (name !== 'createPoint') return;

    after((result: Point) => {
      const marker = circleMarker(result);
      markers.addLayer(marker);
    });
  });

  // Add markers on the map when selecting target and destination coords
  const addMarker = async (result: any, name: any) => {
    let curMarker;

    if (name === 'selectCoords') {
      curMarker = originMarker;
    } else if (name === 'selectDestCoords') {
      curMarker = destMarker;
    }

    if (!curMarker) return;

    if (!result && curMarker.value) {
      return map.removeLayer(curMarker.value);
    } else if (!result) {
      return;
    }

    curMarker.value = targetMarker(result);
    map.addLayer(curMarker.value);
  };

  uiStore.$onAction(({ name, after }) => {
    if (name !== 'selectCoords' && name !== 'selectDestCoords') return;
    after((result: L.LatLng | null) => addMarker(result, name));
  });

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
