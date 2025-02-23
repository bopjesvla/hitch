import {$$} from './utils';

////// Define the search bar for the map //////
export function addGeocoder(map) {
    var geocoderOpts = { "collapsed": true, "defaultMarkGeocode": false, "position": "topleft", "provider": "photon", placeholder: "Jump to city", "zoom": 11 };

    var customGeocoder = L.Control.Geocoder.photon();
    geocoderOpts["geocoder"] = customGeocoder;

    let geocoderController = L.Control.geocoder(
        geocoderOpts
    ).addTo(map);

    let geocoderInput = $$('.leaflet-control-geocoder input')
    geocoderInput.type = 'search'
    let geocoderIcon = $$('.leaflet-control-geocoder-icon')
    geocoderIcon.innerText = ''
    geocoderIcon.classList.add('fa-solid', 'fa-frog')

    geocoderController.on('markgeocode', function (e) {
        var zoom = geocoderOpts['zoom'] || map.getZoom();
        map.setView(e.geocode.center, zoom);
        $$('.leaflet-control-geocoder input').value = ''
    })
}
