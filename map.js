if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js").catch(e => console.error(e));
}

var is_firefox = navigator.userAgent.toLowerCase().indexOf('firefox') > -1;
var is_android = navigator.userAgent.toLowerCase().indexOf("android") > -1;

$$ = function (e) { return document.querySelector(e) }
var points = [], destLines = [], spotMarker, destMarker

var bars = document.querySelectorAll('.sidebar, .topbar')

markerClick = function(e, row, point) {
    if ($$('.topbar.visible') || $$('.sidebar.spot-form-container.visible')) return

    points = [point]

    setTimeout(() => {
        bar('.sidebar.show-spot')
        $$('#spot-header a').href = window.ontouchstart ? `geo:${row[0]},${row[1]}` : ` https://www.google.com/maps/place/${row[0]},${row[1]}`
        $$('#spot-header a').innerText = `${row[0].toFixed(4)}, ${row[1].toFixed(4)}`
        $$('#spot-summary').innerText = `Rating: ${row[2].toFixed(0)}/5
Waiting time in min: ${Number.isNaN(row[4]) ? '-' : row[4].toFixed(0)}
Ride distance in km: ${Number.isNaN(row[5]) ? '-' : row[5].toFixed(0)}`

        $$('#spot-text').innerText = row[3];
        if (!row[3] && Number.isNaN(row[5])) $$('#extra-text').innerHTML = 'No comments/ride info. To hide points like this, check out the <a href=/light.html>lightweight map</a>.'
        else $$('#extra-text').innerHTML = ''

        window.location.hash = `${row[0]},${row[1]}`
    },100)

    for (let d of destLines)
        d.remove()
    destLines = []

    console.log(row)

    if (row[7] != null) {
        for (let i in row[7]) {
            destLines.push(L.polyline([point, [row[7][i], row[8][i]]], {opacity: 0.3, dashArray: '5', color: 'black'}).addTo(map))
        }
    }

    L.DomEvent.stopPropagation(e)
};


function bar(selector) {
    bars.forEach(function (el) {
        el.classList.remove('visible')
    })
    if (selector)
        $$(selector).classList.add('visible')
    if (window.location.hash)
        history.pushState(null, null, ' ')
}

var map = window[$$('.folium-map').id]

$$("input[placeholder^=Search]").placeholder = 'Jump to city'

var AddSpotButton = L.Control.extend({
    options: {
        position: 'topleft'
    },
    onAdd: function (map) {
        var controlDiv = L.DomUtil.create('div', 'leaflet-bar add-spot');
        var container = L.DomUtil.create('a', '', controlDiv);
        container.href = "javascript:void(0);";
        container.innerText = "📍 Add a spot";

        container.onclick = function () {
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

var DonateButton = L.Control.extend({
    options: {
        position: 'bottomright'
    },
    onAdd: function (map) {
        var controlDiv = L.DomUtil.create('div', 'donate-button');
        controlDiv.innerHTML = '<a href="https://en.liberapay.com/Bob./donate"><img alt="Donate using Liberapay" src="https://liberapay.com/assets/widgets/donate.svg"></a>'

        return controlDiv;
    }
});

map.addControl(new AddSpotButton());

if (is_firefox && is_android) document.querySelector('.leaflet-control-geocoder').style.display = 'none';

var zoom = $$('.leaflet-control-zoom')
zoom.parentNode.appendChild(zoom)

// map.addControl(new DonateButton());

$$('#sb-close').onclick = function () {
    bar()
    points = []
    renderPoints()
}

$$('a.step2-help').onclick = e => alert(e.target.title)

var addSpotStep = function (e) {
    if (e.target.tagName != 'BUTTON') return
    if (e.target.innerText == 'Done') {
        let center = map.getCenter()
        if (points[0] && center.distanceTo(points[0]) < 1000 && !confirm("Are you sure this was where the car took you? It's less than 1 km away from the hitchhiking spot."))
            return
        else
            points.push(center)
    }
    if (e.target.innerText.includes("didn't get"))
        points.push(points[0])
    if (e.target.innerText == "Skip")
        points.push({ lat: 'nan', lng: 'nan' })
    renderPoints()
    if (e.target.innerText == 'Done' || e.target.innerText.includes("didn't get") || e.target.innerText.includes('Review') || e.target.innerText == "Skip") {
        if (points.length == 1) {
            if (map.getZoom() > 9) map.setZoom(9);
            map.panTo(points[0])
            bar('.topbar.step2')
        }
        else if (points.length == 2) {
            if (points[1].lat !== 'nan') {
                var bounds = new L.LatLngBounds(points);
                map.fitBounds(bounds, {})
            }
            map.setZoom(map.getZoom() - 1)
            bar('.sidebar.spot-form-container')
            var dest = points[1].lat !== 'nan' ? `${points[1].lat.toFixed(4)}, ${points[1].lng.toFixed(4)}` : 'unknown destination'
            $$('.sidebar.spot-form-container p.greyed').innerText = `${points[0].lat.toFixed(4)}, ${points[0].lng.toFixed(4)} → ${dest}`
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

bars.forEach(bar => bar.onclick = addSpotStep)

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
    if (!added && $$('.sidebar.visible') && !$$('.sidebar.spot-form-container.visible')) {
        points = []
        renderPoints()
        bar()
    }

    L.DomEvent.stopPropagation(e)
})

map.on('zoom', e => {
    let currentOpacity = +window.getComputedStyle($$('.leaflet-overlay-pane')).getPropertyValue("opacity");
    if (map.getZoom() < 9 && currentOpacity == 1) $$('.leaflet-overlay-pane').style.opacity = 0.5
    if (map.getZoom() >= 9 && currentOpacity == 0.5) $$('.leaflet-overlay-pane').style.opacity = 1
})

function renderPoints() {
    if (spotMarker) map.removeLayer(spotMarker)
    if (destMarker) map.removeLayer(destMarker)
    spotMarker = destMarker = null
    if (points[0]) {
        spotMarker = L.marker(points[0])
        spotMarker.addTo(map)
    }
    if (points[1] && points[1].lat !== 'nan') {
        destMarker = L.marker(points[1], { color: 'red' })
        destMarker.addTo(map)
    }
    $$('.leaflet-overlay-pane').style.opacity = points.length ? 0.3 : 1

    if (!points[0]) {
        for (let d of destLines)
            d.remove()
        destLines = []
    }
}
var c = $$('.leaflet-control-attribution')
c.innerHTML = '&copy; Bob de Ruiter | <a href=https://github.com/bopjesvla/hitch>#</a> | <a href=/dump.sqlite>⭳</a> | <a href=recent.html>recent changes</a> <br> Thanks to <a href=https://openstreetmap.org>OSM</a>, <a href=https://leafletjs.com>Leaflet</a> and <a href=https://hitchwiki.org>HitchWiki</a>'
if (window.location.hash == '#success') {
    bar('.sidebar.success')
    history.replaceState(null, null, ' ')
}

function restoreView() {
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
    catch (e) {
        console.warn("Your browser blocks access to " + type);
        return false;
    }
}

if (!window.location.hash.includes(',')) // we'll center on coord
    if (!restoreView.apply(map))
        map.fitBounds([[-35, -40], [60, 40]])
if (map.getZoom() > 13) map.setZoom(13);

$$('.folium-map').focus()
