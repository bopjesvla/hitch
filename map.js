if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js").catch(e => console.error(e));
}

var $$ = function (e) { return document.querySelector(e) }

var addSpotPoints = [],
    planRoutePoints = [],
    addSpotLine = null,
    active = [],
    destLines = [],
    spotMarker,
    destMarker

var bars = document.querySelectorAll('.sidebar, .topbar')

function maybeReportDuplicate(marker) {
    if (document.body.classList.contains('reporting-duplicate')){
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

var markerClick = function(marker) {
    if ($$('.topbar.visible') || $$('.sidebar.spot-form-container.visible')) return

    var row = marker.options._row, point = marker.getLatLng()

    if (row[9] != null) {
        active = allMarkers.filter(m => m.options._row[9] == row[9]).sort(m => m == marker)
    }
    else {
        active = [marker]
    }

    addSpotPoints = []
    renderPoints()

    setTimeout(() => {
        bar('.sidebar.show-spot')
        $$('#spot-header a').href = window.ontouchstart ? `geo:${row[0]},${row[1]}` : ` https://www.google.com/maps/place/${row[0]},${row[1]}`
        $$('#spot-header a').innerText = `${row[0].toFixed(4)}, ${row[1].toFixed(4)} ☍`
        $$('#spot-summary').innerText = `Rating: ${row[2].toFixed(0)}/5
Waiting time: ${Number.isNaN(row[4]) ? '-' : row[4].toFixed(0) + ' min'}
Ride distance: ${Number.isNaN(row[5]) ? '-' : row[5].toFixed(0) + ' km'}`

        $$('#spot-text').innerHTML = row[3];
        if (!row[3] && Number.isNaN(row[5])) $$('#extra-text').innerHTML = 'No comments/ride info. To hide spots like this, check out the <a href=/light.html>lightweight map</a>.'
        else $$('#extra-text').innerHTML = ''
    },100)

    console.log(row)

    if (row[7] != null) {
        for (let i in row[7]) {
            destLines.push(L.polyline([point, [row[7][i], row[8][i]]], {opacity: 0.3, dashArray: '5', color: 'black'}).addTo(map))
        }
    }
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
            clearAllButRoute()
            document.body.classList.add('adding-spot')
            bar('.topbar.spot.step1')

            L.DomEvent.stopPropagation(e)
        }

        return controlDiv;
    }
});

var RouteButton = L.Control.extend({
    options: {
        position: 'topleft'
    },
    onAdd: function (map) {
        var controlDiv = L.DomUtil.create('div', 'leaflet-bar horizontal-button plan-route');
        var container = L.DomUtil.create('a', '', controlDiv);
        container.href = "javascript:void(0);";
        container.innerHTML = "↗️ Plan route";

        container.onclick = function (e) {
            clearAllButRoute()
            document.body.classList.add('planning-route')
            bar('.topbar.route.step1')
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
            clearAllButRoute()
            if (document.body.classList.contains('menu'))
                bar()
            else
                bar('.sidebar.menu')
            document.body.classList.toggle('menu')
            L.DomEvent.stopPropagation(e)
        }

        return controlDiv;
    }
});

var RouteViewButton = L.Control.extend({
    options: {
        position: 'topleft'
    },
    onAdd: function (map) {
        var controlDiv = L.DomUtil.create('div', 'leaflet-bar replacement-button route-view');
        var container = L.DomUtil.create('a', '', controlDiv);
        container.href = "javascript:void(0);";
        container.innerHTML = "<span class='route-view-toggle'></span> Route view";

        container.onclick = function (e) {
            document.body.classList.toggle('directions')
            L.DomEvent.stopPropagation(e)
        }

        return controlDiv;
    }
});

var CancelRouteButton = L.Control.extend({
    options: {
        position: 'topleft'
    },
    onAdd: function (map) {
        var controlDiv = L.DomUtil.create('div', 'leaflet-bar replacement-button cancel-route');
        var container = L.DomUtil.create('a', '', controlDiv);
        container.href = "javascript:void(0);";
        container.innerHTML = "✖ Cancel Route";

        container.onclick = function (e) {
            clearRoute()
            L.DomEvent.stopPropagation(e)
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

// let backpane = map.createPane('back')
// L.imageOverlay('map2.svg', [[-58.49860999999993,-179.9999899999999],[83.62360000,179.99999000000003]], {pane: 'back'}).addTo(map);

// amsterdam to barcelona
// route,52.3051,4.8371,41.3725,2.1766

// lux to metz
// route,49.5429,6.1178,49.1792,6.1768

let directionsLayers = []

let toPoint = coord => L.point(coord.lng, coord.lat)
let toCoord = point => L.latLng(point.y, point.x)
let closest = (coord, segmentStart, segmentEnd) => {
    return toCoord(L.LineUtil.closestPointOnSegment(toPoint(coord), toPoint(segmentStart), toPoint(segmentEnd)))
}

let dirpane = map.createPane('directions')
dirpane.style.zIndex = 450

function planRoute(lat1, lon1, lat2, lon2) {
    let A = new L.LatLng(lat1, lon1), Z = new L.LatLng(lat2, lon2)
    planRoutePoints = [A, Z]
    document.body.classList.add('directions', 'has-route')

    let routeDistance = A.distanceTo(Z)
    // TODO: get the real geographic center?
    let MIDPOINT = L.latLngBounds(A, Z).getCenter()

    for (let d of directionsLayers)
        map.removeLayer(d)

    directionsLayers = [L.polyline([A, Z], {opacity: 0.1, weight: 5, dashArray: '1', color: 'red', pane: 'directions', interactive: false}).addTo(map)]

    for (let spot of destinationMarkers) {
        let B = spot.getLatLng()
        //     AtoB = A.distanceTo(B), BtoZ = B.distanceTo(Z),
        //     detour = AtoB + BtoZ,
        //     stopScore = 2 * routeDistance - Math.abs(AtoB - BtoZ) - detour

        if (MIDPOINT.distanceTo(B) > routeDistance / 1.95 + 10000) continue

        let AtoB = A.distanceTo(B), BtoZ = B.distanceTo(Z)
        let bestImprovement = 0

        let lats = spot.options._destination_lats
        let lons = spot.options._destination_lons

        // loop over the spot's previous rides; don't show all; some have wildly different directions
        for (let i in lats) {
            let rideCoord = new L.LatLng(lats[i], lons[i]),
                closestToZ = closest(Z, B, rideCoord), // what's the point on this ride that is closest to Z?
                improvement = BtoZ - closestToZ.distanceTo(Z), // how much closer to Z would this ride have gotten us?
                travel = B.distanceTo(rideCoord), // how far was this ride?
                retreat = AtoB - A.distanceTo(rideCoord) // how far back to A would this ride have gotten us?

            if (improvement > 0 && retreat < 0.5 * travel) {
                bestImprovement = Math.max(bestImprovement, improvement)

                directionsLayers.push(L.polyline([spot.getLatLng(), rideCoord], {opacity: 0.7, weight: 1, dashArray: '5', color: 'black', pane: 'directions', interactive: false}).addTo(map))
            }
        }
        if (bestImprovement > 0) {
            let marker = new L.circleMarker(B, Object.assign({}, spot.options, {pane: 'directions', radius: 5 + Math.min(bestImprovement / 80000, 5)}))
            marker.on('click', e => spot.fire('click', e))
            marker.addTo(map)
            directionsLayers.push(marker)
        }
    }

    var bounds = new L.LatLngBounds([A, Z]);
    map.fitBounds(bounds, {})
}

var geocoderOpts = {"collapsed": false, "defaultMarkGeocode": false, "position": "topleft", "provider": "photon", placeholder: "Jump to city, search comments", "zoom": 11};

var customGeocoder = L.Control.Geocoder.photon();
geocoderOpts["geocoder"] = customGeocoder;

let geocoderController = L.Control.geocoder(
    geocoderOpts
).addTo(map);

let geocoderInput = $$('.leaflet-control-geocoder input')
geocoderInput.type = 'search'

let oldMarkers = []
let updateRadius = e => {
    let search = geocoderInput.value.toLowerCase()
    let markers = geocoderInput.value.length > 1 ? allMarkers.filter(x => x.options._row[3].toLowerCase().includes(search)) : []
    console.log(markers)
    for (let x of oldMarkers) {
        x.setStyle({radius: 5})
    }
    for (let x of markers) {
        x.setStyle({radius: 10})
        x.bringToFront()
    }
    oldMarkers = markers
}

geocoderInput.addEventListener('input', updateRadius)
geocoderController.on('markgeocode', function(e) {
    var zoom = geocoderOpts['zoom'] || map.getZoom();
    map.setView(e.geocode.center, zoom);
    $$('.leaflet-control-geocoder input').value = ''
    updateRadius()
})
map.addControl(new AddSpotButton());
map.addControl(new RouteButton());
map.addControl(new RouteViewButton());
map.addControl(new CancelRouteButton());
map.addControl(new MenuButton());

var zoom = $$('.leaflet-control-zoom')
zoom.parentNode.appendChild(zoom)

// map.addControl(new DonateButton());

$$('#sb-close').onclick = function (e) {
    clearAllButRoute()
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
        addSpotLine = L.polyline([addSpotPoints[0], map.getCenter()], {opacity: 1, dashArray: '5', color: 'black'}).addTo(map)
    }
    else if (planRoutePoints.length == 1) {
        addSpotLine = L.polyline([planRoutePoints[0], map.getCenter()], {opacity: 1, dashArray: '5', color: 'black'}).addTo(map)
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
        document.body.classList.remove('directions')
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
            var dest = points[1].lat !== 'nan' ? `${points[1].lat.toFixed(4)}, ${points[1].lng.toFixed(4)}` : 'unknown destination'
            $$('.sidebar.spot-form-container p.greyed').innerText = `${points[0].lat.toFixed(4)}, ${points[0].lng.toFixed(4)} → ${dest}`
            $$('#spot-form input[name=coords]').value = `${points[0].lat},${points[0].lng},${points[1].lat},${points[1].lng}`

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
        clearAllButRoute()
    }

    document.body.classList.toggle('adding-spot', addSpotPoints.length > 0)
}

function planRouteStep(e) {
    if (e.target.tagName != 'BUTTON') return
    if (e.target.innerText == 'Done') {
        let center = map.getCenter()
        planRoutePoints.push(center)

        if (planRoutePoints.length == 1) {
            if (map.getZoom() > 7) map.setZoom(7);
            map.panTo(planRoutePoints[0])
            bar('.topbar.route.step2')
        }

        if (planRoutePoints.length == 2) {
            let pr = planRoutePoints
            window.location.hash = `#route,${pr[0].lat},${pr[0].lng},${pr[1].lat},${pr[1].lng}`
        }
    }
    else if (e.target.innerText == 'Cancel') {
        clearRoute()
        clearAllButRoute()
    }
    document.body.classList.toggle('planning-route', planRoutePoints.length > 0)
}

bars.forEach(bar => {
    if (bar.classList.contains('spot')) bar.onclick = addSpotStep
    else if (bar.classList.contains('route')) bar.onclick = planRouteStep
})

map.on('click', e => {
    var added = false;

    if (window.innerWidth < 780) {
        var layerPoint = map.latLngToLayerPoint(e.latlng)
        let markers = document.body.classList.contains('directions') ? directionsLayers.filter(x => x instanceof L.CircleMarker) : allMarkers
        var circles = markers.sort((a, b) => a.getLatLng().distanceTo(e.latlng) - b.getLatLng().distanceTo(e.latlng))
        if (circles[0] && map.latLngToLayerPoint(circles[0].getLatLng()).distanceTo(layerPoint) < 20) {
            added = true
            circles[0].fire('click', e)
        }
    }
    if (!added && !document.body.classList.contains('reporting-duplicate') && $$('.sidebar.visible') && !$$('.sidebar.spot-form-container.visible')) {
        clearAllButRoute()
    }

    L.DomEvent.stopPropagation(e)
})

map.on('zoom', e => {
    document.body.classList.toggle('zoomed-out', map.getZoom() < 9)
})

var oldActive = [];

function renderPoints() {
    if (spotMarker) map.removeLayer(spotMarker)
    if (destMarker) map.removeLayer(destMarker)

    for (let d of destLines)
        d.remove()
    destLines = []

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
    for (let a of active) {
        let lats = a.options._destination_lats
        let lons = a.options._destination_lons
        if (lats && lats.length) {
            for (let i in lats) {
                destLines.push(L.polyline([a.getLatLng(), [lats[i], lons[i]]], {opacity: 0.3, dashArray: '5', color: 'black'}).addTo(map))
            }
        }
    }

    oldActive = active;
}

function clearAllButRoute() {
    if (window.location.hash && !window.location.hash.includes('#route')) {
        window.history.pushState(null, null, ' ')
    }
    if (!window.location.hash) navigate() // clears rest
    else clear()
}
function clear() {
    bar()
    addSpotPoints = []
    active = []
    renderPoints()
    updateAddSpotLine()
    document.body.classList.remove('adding-spot')
    document.body.classList.remove('reporting-duplicate')
}

function clearRoute() {
    document.body.classList.remove('planning-route', 'directions', 'has-route')
    planRoutePoints = []
    if (window.location.hash.includes('#route'))
        window.history.pushState(null, null, ' ')
}

$$('.leaflet-control-attribution').remove()

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

function navigate() {
    console.log(location.hash)

    let args = window.location.hash.split(',')
    if (args[0] == '#route') {
        clear()
        planRoute(+args[1], +args[2], +args[3], +args[4])
    }
    else if (args.length == 2) {
        clear()
        clearRoute()
        let lat = +args[0].slice(1), lon = +args[1]
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
        clearRoute()
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

