import { createApp, reactive } from 'https://unpkg.com/petite-vue?module';

// Store
const store = reactive({
  sidebarVisible: false,
  sidebarSection: '', // 'spotDetail', 'review', 'reviewSuccess'
  selectedSpot: [],
  topbarVisible: false,
  topbarStep: 1,
  points: [],
  spotMarker: null,
  destMarker: null,
});

window.store = store;

// Map
if (window.location.hash == '#success') {
  store.sidebarVisible = true;
  store.sidebarSection = 'reviewSuccess';
  window.location.hash = '#';
}

// Init
createApp({
  store,
}).mount('#app');
