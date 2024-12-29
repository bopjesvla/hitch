import L from 'leaflet';
import 'leaflet.markercluster/dist/leaflet.markercluster.js';

const Map = (function () {
  let map: L.Map;

  const createMap = function () {
    // Initialize Map
    return L.map('map', {
      preferCanvas: true,
      worldCopyJump: true,
      zoomControl: false, // Adding manually for ordering
      minZoom: 1,
    }).setView([51.505, -0.09], 13);
  };

  return {
    getMap: function () {
      if (!map) {
        map = createMap();
      }

      return map;
    }
  }
})();

export default Map;
