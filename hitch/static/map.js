if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js").catch(e => console.error(e));
}

var $$ = function (e) { return document.querySelector(e) }

var addSpotPoints = [],
    addSpotLine = null,
    active = [],
    destLineGroup = null,
    filterDestLineGroup = null,
    filterMarkerGroup = null,
    spotMarker,
    destMarker

var bars = document.querySelectorAll('.sidebar, .topbar')

function maybeReportDuplicate(marker) {
    if (document.body.classList.contains('reporting-duplicate')) {
        var row = marker.options._row, point = marker.getLatLng()

        let activePoint = active[0].getLatLng()

        if (activePoint.equals(point)) {
            alert("A marker cannot be a duplicate of itself.")
            return
        }

        if (confirm(`Are you sure you want to report a duplicate?`)) {
            document.body.innerHTML += `<form id=dupform method=POST action=report-duplicate><input name=report value=${[activePoint.lat, activePoint.lng, row[0], row[1]].join(',')}>`
            document.querySelector('#dupform').submit()
        }
    }
}

function summaryText(row) {
    return `Rating: ${row[2].toFixed(0)}/5
    Waiting time: ${Number.isNaN(row[4]) ? '-' : row[4].toFixed(0) + ' min'}
    Ride distance: ${Number.isNaN(row[5]) ? '-' : row[5].toFixed(0) + ' km'}`
}

function handleMarkerClick(marker, point, e) {
    if ($$('.topbar.visible') || $$('.sidebar.spot-form-container.visible')) return

    maybeReportDuplicate(marker)
    window.location.hash = `${point.lat},${point.lng}`

    L.DomEvent.stopPropagation(e)
}

var markerClick = function (marker) {
    var row = marker.options._row, point = marker.getLatLng()
    active = [marker]

    addSpotPoints = []
    renderPoints()

    setTimeout(() => {
        bar('.sidebar.show-spot')
        $$('#spot-header a').href = window.ontouchstart ? `geo:${row[0]},${row[1]}` : ` https://www.google.com/maps/place/${row[0]},${row[1]}`
        $$('#spot-header a').innerText = `${row[0].toFixed(4)}, ${row[1].toFixed(4)} ☍`

        $$('#spot-summary').innerText = summaryText(row)

        $$('#spot-text').innerHTML = row[3];
        if (!row[3] && Number.isNaN(row[5])) $$('#extra-text').innerHTML = 'No comments/ride info. To hide spots like this, check out the <a href=/light.html>lightweight map</a>.'
        else $$('#extra-text').innerHTML = ''
    }, 100)

    console.log(row)
};


function bar(selector) {
    bars.forEach(function (el) {
        el.classList.remove('visible')
    })
    if (selector)
        $$(selector).classList.add('visible')
}

var map = window[$$('.folium-map').id]

var AddSpotButton = L.Control.extend({
    options: {
        position: 'topleft'
    },
    onAdd: function (map) {
        var controlDiv = L.DomUtil.create('div', 'leaflet-bar horizontal-button add-spot');
        var container = L.DomUtil.create('a', '', controlDiv);
        container.href = "javascript:void(0);";
        container.innerText = "📍 Add spot";

        container.onclick = function (e) {
            if (window.location.href.includes('light')) {
                if (confirm('Do you want to be redirected to the full version where you can add spots?'))
                    window.location = '/'
                return;
            }
            clearParams()
            navigateHome()
            document.body.classList.add('adding-spot')
            bar('.topbar.spot.step1')

            L.DomEvent.stopPropagation(e)
        }

        return controlDiv;
    }
});

var MenuButton = L.Control.extend({
    options: {
        position: 'topleft'
    },
    onAdd: function (map) {
        var controlDiv = L.DomUtil.create('div', 'leaflet-bar horizontal-button menu');
        var container = L.DomUtil.create('a', '', controlDiv);
        container.href = "javascript:void(0);";
        container.innerHTML = "☰";

        container.onclick = function (e) {
          navigateHome();

          if (document.body.classList.contains("menu")) {
            bar();
          } else {
            bar(".sidebar.menu");
          }

          document.body.classList.toggle("menu");
          L.DomEvent.stopPropagation(e);
        };

        return controlDiv;
    }
});

var AccountButton = L.Control.extend({
    options: {
        position: 'topleft'
    },
    onAdd: function (map) {
        var controlDiv = L.DomUtil.create('div', 'leaflet-bar horizontal-button your-account');
        var container = L.DomUtil.create('a', '', controlDiv);
        container.href = "/me";
        container.innerHTML = "👤 Your account";

        return controlDiv;
    }
});

var FilterButton = L.Control.extend({
    options: {
        position: 'topleft'
    },
    onAdd: function (map) {
        var controlDiv = L.DomUtil.create('div', 'leaflet-bar horizontal-button filter-button');
        var container = L.DomUtil.create('a', '', controlDiv);
        container.href = "#filters";
        container.innerHTML = "🧮 Filters";

        return controlDiv;
    }
});

var HeatmapInfoButton = L.Control.extend({
    options: {
        position: 'topleft'
    },
    onAdd: function (map) {
        var controlDiv = L.DomUtil.create('div', 'leaflet-bar horizontal-button heatmap-info');
        var container = L.DomUtil.create('a', '', controlDiv);
        container.href = "javascript:void(0);";
        container.innerHTML = "\u2139 What can I see here?";

        container.onclick = function (e) {
            navigateHome()
            if (document.body.classList.contains('heatmap-info')) {
                bar()
            } else {
                bar('.sidebar.heatmap-info')
            }
            document.body.classList.toggle('heatmap-info')
            L.DomEvent.stopPropagation(e)
        }

        return controlDiv;
    }
});

////// Define the search bar for the map //////
var geocoderOpts = { "collapsed": false, "defaultMarkGeocode": false, "position": "topleft", "provider": "photon", placeholder: "Jump to city, search comments", "zoom": 11 };

var customGeocoder = L.Control.Geocoder.photon();
geocoderOpts["geocoder"] = customGeocoder;

let geocoderController = L.Control.geocoder(
    geocoderOpts
).addTo(map);

let geocoderInput = $$('.leaflet-control-geocoder input')
geocoderInput.type = 'search'

let oldMarkers = []

geocoderController.on('markgeocode', function (e) {
    var zoom = geocoderOpts['zoom'] || map.getZoom();
    map.setView(e.geocode.center, zoom);
    $$('.leaflet-control-geocoder input').value = ''
})

////// Add interaction buttons to the map //////
map.addControl(new MenuButton());
map.addControl(new AddSpotButton());
map.addControl(new AccountButton());
map.addControl(new FilterButton());
if (window.location.pathname === "/hitchhiking.html") {
    map.addControl(new HeatmapInfoButton());
    $$(".filter-button").remove()
    $$(".add-spot").remove()
}

var zoom = $$('.leaflet-control-zoom')
zoom.parentNode.appendChild(zoom)

$$('#sb-close').onclick = function (e) {
    navigateHome()
}

$$('a.step2-help').onclick = e => alert(e.target.title)

$$('.report-dup').onclick = e => document.body.classList.add('reporting-duplicate')
$$('.topbar.duplicate button').onclick = e => document.body.classList.remove('reporting-duplicate')

function updateAddSpotLine() {
    if (addSpotLine) {
        map.removeLayer(addSpotLine)
        addSpotLine = null
    }
    if (addSpotPoints.length == 1) {
        addSpotLine = arrowLine(addSpotPoints[0], map.getCenter()).addTo(map)
    }
}

map.on('move', updateAddSpotLine)

var addSpotStep = function (e) {
    if (e.target.tagName != 'BUTTON') return
    if (e.target.innerText == 'Done') {
        let center = map.getCenter()
        if (addSpotPoints[0] && center.distanceTo(addSpotPoints[0]) < 1000 && !confirm("Are you sure this was where the car took you? It's less than 1 km away from the hitchhiking spot."))
            return
        else
            addSpotPoints.push(center)
    }
    if (e.target.innerText.includes("didn't get"))
        addSpotPoints.push(addSpotPoints[0])
    if (e.target.innerText == "Skip")
        addSpotPoints.push({ lat: 'nan', lng: 'nan' })
    if (e.target.innerText.includes('Review')) {
        addSpotPoints.push(active[0].getLatLng())
        active = []
    }

    renderPoints()

    if (e.target.innerText == 'Done' || e.target.innerText.includes("didn't get") || e.target.innerText.includes('Review') || e.target.innerText == "Skip") {
        if (addSpotPoints.length == 1) {
            if (map.getZoom() > 9) map.setZoom(9);
            map.panTo(addSpotPoints[0])
            bar('.topbar.spot.step2')
        }
        else if (addSpotPoints.length == 2) {
            if (addSpotPoints[1].lat !== 'nan') {
                var bounds = new L.LatLngBounds(addSpotPoints);
                map.fitBounds(bounds, {})
            }
            map.setZoom(map.getZoom() - 1)
            bar('.sidebar.spot-form-container')
            let points = addSpotPoints
            const destinationGiven = points[1].lat !== 'nan'
            var dest = destinationGiven ? `${points[1].lat.toFixed(4)}, ${points[1].lng.toFixed(4)}` : 'unknown destination'
            $$('.sidebar.spot-form-container p.greyed').innerText = `${points[0].lat.toFixed(4)}, ${points[0].lng.toFixed(4)} → ${dest}`
            $$("#no-ride").classList.toggle("make-invisible", destinationGiven);
            $$('#details-seen').classList.add("make-invisible")
            $$('#spot-form input[name=coords]').value = `${points[0].lat},${points[0].lng},${points[1].lat},${points[1].lng}`

            // logic to prevent submitting hidden detailed info
            const form = $$("#spot-form");
            const details = $$("#extended_info");
            const signal = $$("#signal");
            const datetime_ride = $$("#datetime_ride");
            let hasBeenOpen = details.open;

            details.addEventListener("toggle", function () {
                hasBeenOpen = true;
            })

            form.addEventListener("submit", (event) => {
                const hasHiddenFields = signal.value != "null" || datetime_ride.value;
                if (hasHiddenFields && !hasBeenOpen) {
                    $$('#details-seen').classList.remove("make-invisible");
                    hasBeenOpen = details.open = true;
                    event.preventDefault();
                }
            });

            if (storageAvailable('localStorage')) {
                var uname = $$('input[name=username]')
                uname.value = localStorage.getItem('nick')
                uname.onchange = e => localStorage.setItem('nick', uname.value)

                // for (let field of ['males', 'females', 'others', 'signal']) {
                //     let el = $$(`input[name=${field}]`)
                //     el.value = localStorage.getItem(field) || el.value
                //     el.onchange = e => localStorage.setItem(field, uname.value)
                // }
            }
        }
    }
    else if (e.target.innerText == 'Cancel') {
        navigateHome()
    }

    document.body.classList.toggle('adding-spot', addSpotPoints.length > 0)
}

bars.forEach(bar => {
    if (bar.classList.contains('spot')) bar.onclick = addSpotStep
})

map.on('click', e => {
    var added = false;

    if (window.innerWidth < 780) {
        var layerPoint = map.latLngToLayerPoint(e.latlng)
        let markers = document.body.classList.contains('filtering') ? filterMarkerGroup : allMarkers
        var circles = markers.sort((a, b) => a.getLatLng().distanceTo(e.latlng) - b.getLatLng().distanceTo(e.latlng))
        if (circles[0] && map.latLngToLayerPoint(circles[0].getLatLng()).distanceTo(layerPoint) < 20) {
            added = true
            circles[0].fire('click', e)
        }
    }
    if (!added && !document.body.classList.contains('reporting-duplicate') && $$('.sidebar.visible') && !$$('.sidebar.spot-form-container.visible')) {
        navigateHome()
    }

    L.DomEvent.stopPropagation(e)
})

map.on('zoom', e => {
    document.body.classList.toggle('zoomed-out', map.getZoom() < 9)
})

var oldActive = [];

function arrowLine(from, to, opts = {}) {
    return L.polylineDecorator([from, to], {
        patterns: [{
            repeat: 10,
            symbol: L.Symbol.arrowHead({
                pixelSize: 7,
                polygon: true,
                pathOptions: {
                    stroke: false,
                    fill: true,
                    fillOpacity: 0.6,
                    fillColor: 'black',
                    pane: 'arrowlines'
                },
            }),
            offset: 16,
            endOffset: 0
        }
        ]
    })
}

function renderPoints() {
    if (spotMarker) map.removeLayer(spotMarker)
    if (destMarker) map.removeLayer(destMarker)

    if (destLineGroup)
        destLineGroup.remove()

    spotMarker = destMarker = null
    if (addSpotPoints[0]) {
        spotMarker = L.marker(addSpotPoints[0])
        spotMarker.addTo(map)
    }
    if (addSpotPoints[1] && addSpotPoints[1].lat !== 'nan') {
        destMarker = L.marker(addSpotPoints[1], { color: 'red' })
        destMarker.addTo(map)
    }
    document.body.classList.toggle('has-points', addSpotPoints.length)

    destLineGroup = L.layerGroup()

    let opts = document.body.classList.contains('filtering') ? { pane: 'filtering' } : {}

    for (let a of active) {
        let lats = a.options._row[7]
        let lons = a.options._row[8]
        if (lats && lats.length) {
            for (let i in lats) {
                arrowLine(a.getLatLng(), [lats[i], lons[i]], opts).addTo(destLineGroup)
            }
        }
    }

    destLineGroup.addTo(map)

    oldActive = active;
}

function navigateHome() {
    if (window.location.hash) {
        window.history.pushState(null, null, ' ')
    }
    navigate() // clears rest
}

function clear() {
    bar()
    addSpotPoints = []
    active = []
    renderPoints()
    updateAddSpotLine()
    document.body.classList.remove('adding-spot', 'reporting-duplicate', 'menu')
}

$$('.leaflet-control-attribution').innerHTML = `
    © <a href=https://openstreetmap.org/copyright>OpenStreetMap</a>, <a href=https://hitchmap.com/copyright.html>Hitchmap</a> contributors
`

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
if (map.getZoom() > 17 && window.location.hash != '#success-duplicate') map.setZoom(17);

$$('.folium-map').focus()

function exportAsGPX() {
    var script = document.createElement("script");
    script.src = 'https://cdn.jsdelivr.net/npm/togpx@0.5.4/togpx.js';
    script.onload = function () {
        let features = allMarkers.map(m => ({
            "type": "Feature",
            "properties": {
                "text": summaryText(m.options._row) + '\n\n' + m.options._row[3],
                "url": `https://hitchmap.com/${m.options._row[0]},${m.options._row[1]}`
            },
            "geometry": {
                "coordinates": [m.options._row[1], m.options._row[0]],
                "type": "Point"
            }
        }))
        let geojson = {
            type: "FeatureCollection",
            features
        }

        let div = document.createElement('div')
        function toPlainText(html) {
            div.innerHTML = html.replace(/\<(b|h)r\>/g, '\n')
            return div.textContent
        }

        let gpxStr = togpx(geojson, {
            creator: 'Hitchmap',
            featureDescription: f => toPlainText(f.text),
            featureLink: f => f.url
        });

        function downloadGPX(data) {
            const blob = new Blob([data], { type: 'application/gpx+xml' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'hitchmap.gpx';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }

        downloadGPX(gpxStr)
    }
    document.body.appendChild(script)
}

const knob = document.getElementById('knob');
const knobLine = document.getElementById('knobLine');
const knobCone = document.getElementById('knobCone');
const rotationValue = document.getElementById('rotationValue');
const spreadInput = document.getElementById('spreadInput');
spreadInput.value = 70
const knobToggle = document.getElementById('knob-toggle');
const textFilter = document.getElementById('text-filter');
const userFilter = document.getElementById('user-filter');
const distanceFilter = document.getElementById('distance-filter');
const clearFilters = document.getElementById('clear-filters');

let isDragging = false, radAngle = 0;

function setQueryParameter(key, value) {
    const url = new URL(window.location.href); // Get the current URL
    if (value)
        url.searchParams.set(key, value); // Set or update the query parameter
    else
        url.searchParams.delete(key);
    window.history.replaceState({}, '', url.toString()); // Update the URL without reloading
    navigate();
}

function getQueryParameter(key) {
    const url = new URL(window.location.href);
    return url.searchParams.get(key);
}

function clearParams() {
    const url = new URL(window.location.href);
    let newURL = url.origin + url.pathname + url.hash;
    window.history.replaceState({}, '', newURL.toString());
    navigate();
}

clearFilters.onclick = () => {
    clearParams()
    navigateHome()
}

knob.addEventListener('mousedown', (e) => {
    isDragging = true;
    updateRotation(e);
    const angle = Math.round(radAngle * (180 / Math.PI) + 90) % 360;
    const normalizedAngle = (angle + 360) % 360; // Normalize angle
    setQueryParameter('direction', normalizedAngle);
});

window.addEventListener('mousemove', (e) => {
    if (isDragging) {
        updateRotation(e);
        const angle = Math.round(radAngle * (180 / Math.PI) + 90) % 360;
        const normalizedAngle = (angle + 360) % 360; // Normalize angle
        setQueryParameter('direction', normalizedAngle);
    }
});

window.addEventListener('mouseup', () => {
    isDragging = false;
});

spreadInput.addEventListener('input', updateConeSpread);
knobToggle.addEventListener('input', () => setQueryParameter('mydirection', knobToggle.checked));
userFilter.addEventListener('input', () => setQueryParameter('user', userFilter.value));
textFilter.addEventListener('input', () => setQueryParameter('text', textFilter.value));
distanceFilter.addEventListener('input', () => setQueryParameter('mindistance', distanceFilter.value));

let filterPane = map.createPane('filtering')
filterPane.style.zIndex = 450

let arrowlinePane = map.createPane('arrowlines')
filterPane.style.zIndex = 1450

function updateRotation(event) {
    const rect = knob.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    const dx = event.clientX - centerX;
    const dy = event.clientY - centerY;

    radAngle = Math.atan2(dy, dx);
}

function updateConeSpread() { // Clamp spread between 1 and 89
    const spread = Math.min(89, parseInt(spreadInput.value, 10) || 0);

    if (spread > 0)
        setQueryParameter('spread', spread);
}

function applyParams() {
    const normalizedAngle = parseFloat(getQueryParameter('direction'));
    const spread = parseFloat(getQueryParameter('spread')) || 70;

    if (!isNaN(normalizedAngle)) {
        knobLine.style.transform = `translateX(-50%) rotate(${normalizedAngle}deg)`;
        knobCone.style.transform = `rotate(${normalizedAngle}deg)`;
        rotationValue.textContent = `${Math.round(normalizedAngle)}°`;
        radAngle = (normalizedAngle - 90) * (Math.PI / 180); // Update radAngle for consistency
    }

    spreadInput.value = spread;
    const radiansSpread = spread * (Math.PI / 180); // Convert spread angle to radians

    const multiplier = 100; // Factor to increase the cone's distance

    // Calculate cone boundaries using trigonometry and multiply by the multiplier
    const leftX = 50 - Math.sin(radiansSpread) * 50 * multiplier; // 50 is the radius
    const rightX = 50 + Math.sin(radiansSpread) * 50 * multiplier;
    const topY = 50 - Math.cos(radiansSpread) * 50 * multiplier; // Top vertex

    knobCone.style.clipPath = `polygon(50% 50%, ${leftX}% ${topY}%, ${rightX}% ${topY}%)`;

    knobToggle.checked = getQueryParameter('mydirection') == 'true'
    textFilter.value = getQueryParameter('text')
    userFilter.value = getQueryParameter('user')
    distanceFilter.value = getQueryParameter('mindistance')

    if (knobToggle.checked || textFilter.value || userFilter.value || distanceFilter.value) {
        if (filterMarkerGroup) filterMarkerGroup.remove()
        if (filterDestLineGroup) filterDestLineGroup.remove()

        let filterMarkers = knobToggle.checked || distanceFilter.value ? destinationMarkers : allMarkers;
        // display filters pane
        document.body.classList.add('filtering')

        if (userFilter.value) {
            filterMarkers = filterMarkers.filter(
                marker => marker.options._row[6] && marker.options._row[6]
                    .map(x => x.toLowerCase())
                    .includes(userFilter.value.toLowerCase())
            )
        }
        if (textFilter.value) {
            filterMarkers = filterMarkers.filter(
                x => x.options._row[3].toLowerCase().includes(textFilter.value.toLowerCase())
            )
        }
        if (distanceFilter.value) {
            filterMarkers = filterMarkers.filter(
                x => {
                    let from = x.getLatLng()
                    let lats = x.options._row[7]
                    let lons = x.options._row[8]

                    for (let i in lats) {
                        // Road distance is on average 25% longer than straight distance
                        if (from.distanceTo([lats[i], lons[i]]) * 1.25 / 1000 > distanceFilter.value)
                            return true
                    }
                    return false
                }
            )
        }
        if (knobToggle.checked) {
            filterMarkers = filterMarkers.filter(
                x => {
                    let from = x.getLatLng()
                    let lats = x.options._row[7]
                    let lons = x.options._row[8]

                    for (let i in lats) {
                        let travelAngle = Math.atan2(from.lat - lats[i], lons[i] - from.lng);
                        // difference between the travel direction and the cone line
                        let coneLineDiff = Math.abs(travelAngle - radAngle)
                        let wrappedDiff = Math.min(coneLineDiff, 2 * Math.PI - coneLineDiff)
                        // if the direction falls within the knob's cone
                        if (wrappedDiff < radiansSpread)
                            return true
                    }
                    return false
                }
            )
        }

        // duplicate all markers to the filtering pane
        filterMarkers = filterMarkers.map(
            spot => {
                let loc = spot.getLatLng()
                let marker = new L.circleMarker(loc, Object.assign({}, spot.options, { pane: 'filtering' }))
                marker.on('click', e => spot.fire('click', e))
                return marker
            }
        )

        filterMarkerGroup = L.layerGroup(
            filterMarkers, { pane: 'filtering' }
        ).addTo(map)
    } else {
        document.body.classList.remove('filtering')
    }
}

// Initialize the cone spread and knob appearance
applyParams();

function navigate() {
    applyParams();

    let args = window.location.hash.slice(1).split(',')
    if (args[0] == 'route') {
        clear()
        planRoute(+args[1], +args[2], +args[3], +args[4])
    }
    else if (args[0] == 'location') {
        clear()
        map.setView([+args[1], +args[2]], args[3])
    }
    else if (args[0] == 'filters') {
        clear()
        bar('.sidebar.filters')
    }
    else if (args.length == 2 && !isNaN(args[0])) {
        console.log('YEAH')
        clear()
        let lat = +args[0], lon = +args[1]
        for (let m of allMarkers) {
            if (m._latlng.lat === lat && m._latlng.lng === lon) {
                markerClick(m)
                if (map.getZoom() < 3)
                    map.setView(m.getLatLng(), 16)
                return
            }
        }
    }
    else {
        clear()
    }
}

window.onhashchange = navigate

navigate()

if (window.location.hash == '#success') {
    history.replaceState(null, null, ' ')
    bar('.sidebar.success')
}

if (window.location.hash == '#success-duplicate') {
    history.replaceState(null, null, ' ')
    bar('.sidebar.success-duplicate')
}

if (window.location.hash == '#failed') {
    history.replaceState(null, null, ' ')
    bar('.sidebar.failed')
}

if (window.location.hash == '#registered') {
    history.replaceState(null, null, ' ')
    bar('.sidebar.registered')
}
