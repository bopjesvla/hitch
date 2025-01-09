import Geocoder, { geocoders } from 'leaflet-control-geocoder';

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
  }
}

// var geocoderOpts = {
//   provider: 'photon',
//   zoom: 11,
// };

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

// geocoderInput.addEventListener('input', updateRadius)
// geocoderController.on('markgeocode', function (e) {
//     var zoom = geocoderOpts['zoom'] || map.getZoom();
//     map.setView(e.geocode.center, zoom);
//     $$('.leaflet-control-geocoder input').value = ''
//     updateRadius()
// })
