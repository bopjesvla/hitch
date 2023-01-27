if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js").catch(e => console.error(e));
}

var is_firefox = navigator.userAgent.toLowerCase().indexOf('firefox') > -1;
var is_android = navigator.userAgent.toLowerCase().indexOf("android") > -1;

$$ = function(e) {return document.querySelector(e)}
var points = [], spotMarker, destMarker

document.addEventListener("DOMContentLoaded", function() {
    var RestoreViewMixin = {
        restoreView: function () {
            if (!storageAvailable('localStorage')) {
                return false;
            }
            var storage = window.localStorage;
            if (!this.__initRestore) {
                this.on('moveend', function (e) {
                    if (!this._loaded)
                        return;  // Never access map bounds if view is not set.

                    var view = {
                        lat: this.getCenter().lat,
                        lng: this.getCenter().lng,
                        zoom: this.getZoom()
                    };
                    storage['mapView'] = JSON.stringify(view);
                }, this);
                this.__initRestore = true;
            }

            var view = storage['mapView'];
            try {
                view = JSON.parse(view || '');
                this.setView(L.latLng(view.lat, view.lng), view.zoom, true);
                return true;
            }
            catch (err) {
                return false;
            }
        }
    };

    function storageAvailable(type) {
        try {
            var storage = window[type],
                x = '__storage_test__';
            storage.setItem(x, x);
            storage.removeItem(x);
            return true;
        }
        catch(e) {
            console.warn("Your browser blocks access to " + type);
            return false;
        }
    }

    var map = window[$$('.folium-map').id]

    $$("input[placeholder^=Search]").placeholder = 'Jump to city'
    document.body.insertAdjacentHTML('beforeend',
        '<div id="sidebar"></div><a href="#" id="sb-close">&times;</a><div id="topbar">')

    var customControl =  L.Control.extend({
        options: {
            position: 'topleft'
        },
        onAdd: function (map) {
            var controlDiv = L.DomUtil.create('div', 'leaflet-bar add-spot');
            var container = L.DomUtil.create('a', '', controlDiv);
            container.href="#";
            container.innerText = "📍 Add a spot";

            container.onclick = function() {
                if (window.location.href.includes('light')) {
                    if (confirm('Do you want to be redirected to the full version where you can add spots?'))
                        window.location = '/'
                    return;
                }
                // document.body.classList.add('picker-mode')
                $$('#topbar').innerHTML = '<span>Zoom the crosshairs into your hitchhiking spot. Be as precise as possible!</span><br><button>Done</button><button>Cancel'
                points = []
                renderPoints()
            }

            return controlDiv;
        }
    });

    map.addControl(new customControl());

    if(is_firefox && is_android) document.querySelector('.leaflet-control-geocoder').style.display = 'none';

    // $$('.leaflet-top.leaflet-left').insertAdjacentHTML('beforeend', '<div id="add-spot" class="leaflet-bar leaflet-control"><a href="#">📍 Add a spot')
    var zoom = $$('.leaflet-control-zoom')
    zoom.parentNode.appendChild(zoom)

    $$('#sb-close').onclick = function() {
        $$('#sidebar').replaceChildren()
        points = []
        renderPoints()
    }
    var addWizard = function(e) {
        if (e.target.tagName != 'BUTTON') return
        if (e.target.innerText == 'Done')
            points.push(map.getCenter())
        if (e.target.innerText.includes("didn't get"))
            points.push(points[0])
        renderPoints()
        if (e.target.innerText == 'Done' || e.target.innerText.includes("didn't get") || e.target.innerText.includes('Review')) {
            if (points.length == 1) {
                if(map.getZoom() > 13) map.setZoom(13);
                $$('#topbar').innerHTML = "<span>Move the crosshairs to the city/area you were dropped off when you used this spot. This does not have to be precise.<sup><a href=# class=help>?</a></sup></span><br><button>Done</button><button>I didn't get a ride</button><button>Cancel"
                $$('#sidebar').innerHTML = ''
                $$('a.help').onclick = _ => alert('This is mostly used for distance and direction statistics, so it does not have to precise. If you were dropped off at multiple locations when using this spot, either choose something in the middle or leave multiple reviews.')
            }
            else if (points.length == 2) {
                var bounds = new L.LatLngBounds(points);
                map.fitBounds(bounds, {paddingBottomRight: [0, 400]})
                map.setZoom(map.getZoom() - 1)
                $$('#topbar').innerHTML = '';
                $$('#sidebar').innerHTML = `<h3>New Review</h3>
                                            <p class=greyed>${points[0].lat.toFixed(4)}, ${points[0].lng.toFixed(4)} → ${points[1].lat.toFixed(4)}, ${points[1].lng.toFixed(4)}</p>
                                            <form id=spot-form action=experience method=post>
                                              <input type="hidden" name="coords" value='${points[0].lat},${points[0].lng},${points[1].lat},${points[1].lng}' >
                                              <label>How do you rate the spot?</label>
                                              <div class="clear"><div class="rate">
                                                  <input required type="radio" id="star5" name="rate" value="5" />
                                                  <label for="star5" title="5 stars">5 stars</label>
                                                  <input type="radio" id="star4" name="rate" value="4" />
                                                  <label for="star4" title="4 stars">4 stars</label>
                                                  <input type="radio" id="star3" name="rate" value="3" />
                                                  <label for="star3" title="3 stars">3 stars</label>
                                                  <input type="radio" id="star2" name="rate" value="2" />
                                                  <label for="star2" title="2 stars">2 stars</label>
                                                  <input type="radio" id="star1" name="rate" value="1" />
                                                  <label for="star1" title="1 star">1 star</label>
                                              </div></div>
                                              <label>How long did you wait? Leave blank if you don't remember.</label>
                                              <input type="number" name="wait"> minutes
                                              <label>Optional comment</label>
                                              <div><textarea name=comment></textarea></div>
                                              <label>Public nickname (alphanumeric)</label>
                                              <input name="username">
                                              <input type="submit" value="Submit">
`;

                if(storageAvailable('localStorage')) {
                    var uname = $$('input[name=username]')
                    uname.value = localStorage.getItem('nick')
                    uname.onchange = e => localStorage.setItem('nick', uname.value)
                }
            }
        }
        else if (e.target.innerText == 'Cancel') {
            points = []; $$('#topbar').innerHTML = ''; renderPoints();
        }
    }
    $$('#topbar').onclick = addWizard
    $$('#sidebar').onclick = addWizard

    map.on('click', e => {
        var added = false;

        if (window.innerWidth < 780) {
            var layerPoint = map.latLngToLayerPoint(e.latlng)
            var circles = Object.values(map._layers).filter(x => x instanceof L.CircleMarker).sort((a, b) => a.getLatLng().distanceTo(e.latlng) - b.getLatLng().distanceTo(e.latlng))
            if (circles[0] && map.latLngToLayerPoint(circles[0].getLatLng()).distanceTo(layerPoint) < 200) {
                added = true
                circles[0].fire('click', e)
            }
        }
        if (!added && !$$('#sidebar form'))
            $$('#sidebar').innerHTML = ''

        L.DomEvent.stopPropagation(e)
    })

    function renderPoints() {
        if (spotMarker) map.removeLayer(spotMarker)
        if (destMarker) map.removeLayer(destMarker)
        spotMarker = destMarker = null
        if (points[0]) {
            spotMarker = L.marker(points[0])
            spotMarker.addTo(map)
        }
        if (points[1]) {
            destMarker = L.marker(points[1], {color: 'red'})
            destMarker.addTo(map)
        }
        $$('.leaflet-overlay-pane').style.opacity = points.length ? 0.3 : 1
    }
    var c = $$('.leaflet-control-attribution')
    c.innerHTML = '&copy; Bob de Ruiter | <a href=https://github.com/bopjesvla/hitch>#</a> | <a href=/dump.sqlite>⭳</a> | ' + c.innerHTML.split(',')[0].replace('© ', '').replace('OpenStreetMap', 'OSM').replace('Leaflet', 'L') + ' and <a href=https://hitchwiki.org>HitchWiki</a>'
    if (window.location.hash == '#success') {
        $$('#sidebar').innerHTML = '<h3>Success!</h3>Your review will appear on the map within 10 minutes. Refreshing may be needed.'
        window.location.hash = '#'
    }

    if(!RestoreViewMixin.restoreView.apply(map))
        map.fitBounds([[-35, -40], [60, 40]])
    if(map.getZoom() > 13) map.setZoom(13);
})
