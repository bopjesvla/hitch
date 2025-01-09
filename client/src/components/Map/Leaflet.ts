import L from 'leaflet';
import 'leaflet.markercluster/dist/leaflet.markercluster.js';
import 'leaflet-control-geocoder';

import { INITIAL_POS, INITIAL_ZOOM } from './MapConstants';

const Map = (function () {
  let map: L.Map;

  const createMap = function () {
    // Initialize Map
    return L.map('map', {
      preferCanvas: true,
      worldCopyJump: true,
      zoomControl: false, // Adding manually for ordering
      minZoom: 1,
    }).setView(INITIAL_POS, INITIAL_ZOOM);
  };

  return {
    getMap: function () {
      if (!map) {
        map = createMap();
      }

      return map;
    },
  };
})();

export default Map;
export { L };
