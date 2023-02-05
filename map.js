if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js").catch(e => console.error(e));
}

var is_firefox = navigator.userAgent.toLowerCase().indexOf('firefox') > -1;
var is_android = navigator.userAgent.toLowerCase().indexOf("android") > -1;

$$ = function(e) {return document.querySelector(e)}
var points = [], spotMarker, destMarker

var bars = document.querySelectorAll('.sidebar, .topbar')

function bar(selector) {
    bars.forEach(function(el) {
        el.classList.remove('visible')
    })
    if(selector)
        $$(selector).classList.add('visible')
}

var map = window[$$('.folium-map').id]

$$("input[placeholder^=Search]").placeholder = 'Jump to city'

var AddSpotButton =  L.Control.extend({
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
            bar('.topbar.step1')
            points = []
            renderPoints()
        }

        return controlDiv;
    }
});

map.addControl(new AddSpotButton());

if(is_firefox && is_android) document.querySelector('.leaflet-control-geocoder').style.display = 'none';

// $$('.leaflet-top.leaflet-left').insertAdjacentHTML('beforeend', '<div id="add-spot" class="leaflet-bar leaflet-control"><a href="#">📍 Add a spot')
var zoom = $$('.leaflet-control-zoom')
zoom.parentNode.appendChild(zoom)

$$('#sb-close').onclick = function() {
    bar()
    points = []
    renderPoints()
}

$$('a.step2-help').onclick = _ => alert(e.target.title)

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
            bar('.topbar.step2')
        }
        else if (points.length == 2) {
            var bounds = new L.LatLngBounds(points);
            map.fitBounds(bounds, {paddingBottomRight: [0, 400]})
            map.setZoom(map.getZoom() - 1)
            bar('.sidebar.spot-form-container')
            $$('.sidebar.spot-form-container p.greyed').innerText = `${points[0].lat.toFixed(4)}, ${points[0].lng.toFixed(4)} → ${points[1].lat.toFixed(4)}, ${points[1].lng.toFixed(4)}`
            $$('#spot-form input[name=coords]').value = `${points[0].lat},${points[0].lng},${points[1].lat},${points[1].lng}`

            if (storageAvailable('localStorage')) {
                var uname = $$('input[name=username]')
                uname.value = localStorage.getItem('nick')
                uname.onchange = e => localStorage.setItem('nick', uname.value)
            }
        }
    }
    else if (e.target.innerText == 'Cancel') {
        points = []; bar(); renderPoints();
    }
}

bars.forEach(bar => bar.onclick = addWizard)

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
    if (!added && $$('.sidebar.visible') && !$$('.sidebar.spot-form-container.visible'))
        bar()

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
    bar('.sidebar.success')
    window.location.hash = '#'
}

function restoreView () {
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

if(!restoreView.apply(map))
    map.fitBounds([[-35, -40], [60, 40]])
if(map.getZoom() > 13) map.setZoom(13);

$$('.folium.map').focus()
