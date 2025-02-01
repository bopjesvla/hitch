import {$$} from './utils';

////// Define the search bar for the map //////
export function addGeocoder(map) {
    var geocoderOpts = { "collapsed": false, "defaultMarkGeocode": false, "position": "topleft", "provider": "photon", placeholder: "Jump to city, search comments", "zoom": 11 };

    var customGeocoder = L.Control.Geocoder.photon();
    geocoderOpts["geocoder"] = customGeocoder;

    let geocoderController = L.Control.geocoder(
        geocoderOpts
    ).addTo(map);

    let geocoderInput = $$('.leaflet-control-geocoder input')
    geocoderInput.type = 'search'

    geocoderController.on('markgeocode', function (e) {
        var zoom = geocoderOpts['zoom'] || map.getZoom();
        map.setView(e.geocode.center, zoom);
        $$('.leaflet-control-geocoder input').value = ''
    })
}
