import Geocoder, { geocoders } from 'leaflet-control-geocoder';
import Map from '../Leaflet';

export default class SearchInput extends Geocoder {
  constructor() {
    super();

    this.options = {
      ...this.options,
      collapsed: false,
      // defaultMarkGeocode: false,
      position: 'topleft',
      placeholder: 'Jump to city, search comments',
      geocoder: geocoders.photon(),
    };

    // TODO: When typing, highlight points with relevant comments (old code below)
    // (UI for this isn't super obvious, I didn't know it was possible...)
    // - Leon, 9.1.2025

    this.markGeocode = (e) => {
      const map = Map.getMap();
      map.setView(e.geocode.center, map.getZoom() || 11);

      // Reset query
      this.setQuery("");

      // TODO: Highlight points (see above)

      return this;
    };
  }
}

// let oldMarkers = []
// let updateRadius = e => {
//     let search = geocoderInput.value.toLowerCase()
//     let markers = geocoderInput.value.length > 1 ? allMarkers.filter(x => x.options._row[3].toLowerCase().includes(search)) : []
//     console.log(markers)
//     for (let x of oldMarkers) {
//         x.setStyle({ radius: 5 })
//     }
//     for (let x of markers) {
//         x.setStyle({ radius: 10 })
//         x.bringToFront()
//     }
//     oldMarkers = markers
// }
