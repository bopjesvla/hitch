import L from 'leaflet';
import 'leaflet.markercluster/dist/leaflet.markercluster.js';
import 'leaflet-control-geocoder';

import { useUiStore } from '@/stores/ui';

const Map = (function () {
  let map: L.Map;

  const createMap = () => {
    const uiStore = useUiStore();
    uiStore.parseHash();

    // Initialize Map
    return L.map('map', {
      preferCanvas: true,
      worldCopyJump: true,
      zoomControl: false, // Adding manually for ordering
      minZoom: 1,
    }).setView(uiStore.currentPos, uiStore.currentZoom);
  };

  return {
    getMap: () => {
      if (!map) {
        map = createMap();
      }

      return map;
    },
  };
})();

export default Map;
export { L };
