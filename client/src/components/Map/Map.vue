<template>
  <div v-if="isLoading" class="LoadingIndicator">Loading...</div>
  <MapAction v-if="currentMapAction" />
  <div :class="currentZoom < 9 || originMarker || destMarker ? 'Map--dimmed' : ''">
    <div id="map"></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, shallowRef } from 'vue';
import L from 'leaflet';
import Map from './Leaflet.ts';

import SearchInput from './Controls/SearchInput';
import AddSpotButton from './Controls/AddSpotButton';
import MenuButton from './Controls/MenuButton';
// import RouteButton from './Controls/RouteButton';

import MapAction from './MapAction.vue';

// Stores
import { usePointsStore, type Point } from '@/stores/points';
import { COLOR_BY_RATING, OPACITY_BY_RATING } from './MapConstants';
import { useUiStore } from '@/stores/ui';
import { storeToRefs } from 'pinia';

const pointsStore = usePointsStore();
const uiStore = useUiStore();

const { currentMapAction, currentComponent, currentZoom } = storeToRefs(uiStore);
const isLoading = computed(() => pointsStore.isLoading);
const points = computed(() => pointsStore.items);

const originMarker = shallowRef<L.Marker>();
const destMarker = shallowRef<L.Marker>();

const targetMarker = (point: L.LatLng) => L.marker(point);

const circleMarker = (point: Point) =>
  L.circleMarker(L.latLng(point.Latitude, point.Longitude), {
    radius: 5,
    weight: point.ReviewCount ? 1 + (point.ReviewCount > 2 ? 1 : 0) : 1,
    color: 'black',
    fillOpacity: OPACITY_BY_RATING[point.Rating as keyof typeof OPACITY_BY_RATING],
    fillColor: COLOR_BY_RATING[point.Rating as keyof typeof COLOR_BY_RATING],
    bubblingMouseEvents: false,
  });

onMounted(async () => {
  const map = Map.getMap();

  // Initialize Controls
  L.control.scale().addTo(map);

  new SearchInput().addTo(map);
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

    marker.on('click', async () => {
      if (uiStore.currentMapAction === 'MarkDuplicate') {
        const confirmed = confirm('Are you sure you want to report a duplicate?');

        if (!confirmed) return;

        await pointsStore.markDuplicate(point);
        return uiStore.openSidebar('DuplicateSubmitted');
      }

      pointsStore.selectPoint(point);
      uiStore.openSidebar('ViewSpot');
    });

    markers.addLayer(marker);
  });

  map.addLayer(markers);

  map.on('zoom', () => {
    uiStore.setZoom(map.getZoom());
  });

  map.on('moveend', () => {
    uiStore.setPos(map.getCenter());
  });

  // When clicking on map, close sidebar unless the user is actively editing.
  map.on('click', () => {
    if (currentMapAction.value || currentComponent.value === 'AddSpotForm') return;
    uiStore.closeSidebar();
  });

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
    if (name == 'selectCoords' || name == 'selectDestCoords') {
      return after((result: L.LatLng | null) => addMarker(result, name));
    }

    if (name == 'setPos' || name == 'setZoom') {
      return after(uiStore.setHash);
    }
  });

  // TODO: Center on Coords if available
  // if (!window.location.hash.includes(',')) {
  //   map.fitBounds;
  // }
});
</script>

<style scoped>
.LoadingIndicator,
#map {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.LoadingIndicator {
  @apply flex text-center text-xl z-30 bg-black/50 text-white items-center justify-center;
}
</style>
