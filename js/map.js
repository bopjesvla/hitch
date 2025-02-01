import {addGeocoder} from './geocoder'
import {exportAsGPX} from './export-gpx';
import {$$, bar, bars, arrowLine} from './utils';
import {clearParams, applyParams, filterMarkerGroup} from './filters';
import {restoreView, storageAvailable, summaryText} from './utils';

// Register service worker for offline functionality
if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js").catch(e => console.error(e));
}

// Initialize global variables for spot tracking
var addSpotPoints = [], // Array to store points when adding new spots
    addSpotLine = null, // Line connecting spots
    active = [], // Currently active/selected markers
    destLineGroup = null, // Group for destination lines
    spotMarker, // Marker for hitchhiking spot
    destMarker // Marker for destination

// Handle reporting of duplicate spots
function maybeReportDuplicate(marker) {
    if (document.body.classList.contains('reporting-duplicate')) {
        var row = marker.options._row, point = marker.getLatLng()

        let activePoint = active[0].getLatLng()

        // Prevent self-reporting as duplicate
        if (activePoint.equals(point)) {
            alert("A marker cannot be a duplicate of itself.")
            return
        }

        // Confirm and submit duplicate report
        if (confirm(`Are you sure you want to report a duplicate?`)) {
            document.body.innerHTML += `<form id=dupform method=POST action=report-duplicate><input name=report value=${[activePoint.lat, activePoint.lng, row[0], row[1]].join(',')}>`
            document.querySelector('#dupform').submit()
        }
    }
}

// Handle marker click events
function handleMarkerClick(marker, point, e) {
    // Prevent interaction if certain UI elements are visible
    if ($$('.topbar.visible') || $$('.sidebar.spot-form-container.visible')) return

    maybeReportDuplicate(marker)
    window.location.hash = `${point.lat},${point.lng}`

    L.DomEvent.stopPropagation(e)
}

// Handle navigation to a marker
var handleMarkerNavigation = function (marker) {
    var row = marker.options._row, point = marker.getLatLng()
    active = [marker]

    addSpotPoints = []
    renderPoints()

    // Update sidebar with spot information
    setTimeout(() => {
        bar('.sidebar.show-spot')
        // Create location link based on device type (mobile vs desktop)
        $$('#spot-header a').href = window.ontouchstart ? `geo:${row[0]},${row[1]}` : ` https://www.google.com/maps/place/${row[0]},${row[1]}`
        $$('#spot-header a').innerText = `${row[0].toFixed(4)}, ${row[1].toFixed(4)} ☍`

        $$('#spot-summary').innerText = summaryText(row)

        // Handle spot description and additional info
        $$('#spot-text').innerHTML = row[3];
        if (!row[3] && Number.isNaN(row[5]))
            $$('#extra-text').innerHTML = 'No comments/ride info. To hide spots like this, check out the <a href=/light.html>lightweight map</a>.'
        else
            $$('#extra-text').innerHTML = ''
    }, 100)
};

// Take map from Folium, which was created in scripts/show.py
var map = window[$$('.folium-map').id]

// Create custom map panes for layering
let filterPane = map.createPane('filtering')
filterPane.style.zIndex = 450

let arrowlinePane = map.createPane('arrowlines')
filterPane.style.zIndex = 1450

// Add geocoding functionality
addGeocoder(map)

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
            navigateHome()
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

////// Add interaction buttons to the map //////
map.addControl(new MenuButton());
map.addControl(new AddSpotButton());
map.addControl(new AccountButton());
map.addControl(new FilterButton());

// Put zoom control last
var zoom = $$('.leaflet-control-zoom')
zoom.parentNode.appendChild(zoom)

$$('#sb-close').onclick = function (e) {
    navigateHome()
}

$$('a.step2-help').onclick = e => alert(e.target.title)

$$('.report-dup').onclick = e => document.body.classList.add('reporting-duplicate')
$$('.topbar.duplicate button').onclick = e => document.body.classList.remove('reporting-duplicate')

// Update visual line connecting spots
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

// Handle multi-step spot addition process
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
            // nicknames wont be recorded if a user is logged in
            fetch('/user')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('HTTP error! Status:');
                    }
                    return response.json(); // Parse the JSON response
                })
                .then(data => {
                    $$("#nickname-container").classList.toggle("make-invisible", data.logged_in);
                })
                .catch(error => {
                    console.error('Error fetching user info:', error);
                });
            $$('#spot-form input[name=coords]').value = `${points[0].lat},${points[0].lng},${points[1].lat},${points[1].lng}`

            // logic to prevent submitting hidden detailed info
            const form = $$("#spot-form");
            form.reset();

            if (storageAvailable('localStorage')) {
                var uname = $$('input[name=username]')
                uname.value = localStorage.getItem('nick')
                uname.onchange = e => localStorage.setItem('nick', uname.value)
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

// Map click handler for mobile optimization
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

    for (let a of active) {
        let lats = a.options._row[7]
        let lons = a.options._row[8]
        if (lats && lats.length) {
            for (let i in lats) {
                arrowLine(a.getLatLng(), [lats[i], lons[i]]).addTo(destLineGroup)
            }
        }
    }

    destLineGroup.addTo(map)
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

if (!window.location.hash.includes(',')) // we'll center on coord
    if (!restoreView.apply(map))
        map.fitBounds([[-35, -40], [60, 40]])
if (map.getZoom() > 17 && window.location.hash != '#success-duplicate') map.setZoom(17);

$$('.folium-map').focus()

// validate add spot form input
document.getElementById('spot-form').addEventListener('submit', function(event) {
    const nicknameInput = document.getElementById('nickname-input');
    if (nicknameInput.value != ""){
        event.preventDefault();
        const errorMessage = document.getElementById('nickname-error-message');
        errorMessage.textContent = '';

        // nicknames that are used as usernames are not allowed
        let url = '/is_username_used/' + nicknameInput.value;
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('HTTP error! Status:');
                }
                return response.json(); // Parse the JSON response
            })
            .then(data => {
                if (data.used){
                    errorMessage.textContent = 'This nickname is already used by a registered user. Please choose another nickname.';
                } else {
                    this.submit();
                }
            })
            .catch(error => {
                console.error('Error fetching user info:', error);
            });
    };
});

function navigate() {
    applyParams();

    let args = window.location.hash.slice(1).split(',')
    if (args[0] == 'location') {
        clear()
        map.setView([+args[1], +args[2]], args[3])
    }
    else if (args[0] == 'filters') {
        clear()
        bar('.sidebar.filters')
    }
    else if (args.length == 2 && !isNaN(args[0])) {
        clear()
        let lat = +args[0], lon = +args[1]
        for (let m of allMarkers) {
            if (m._latlng.lat === lat && m._latlng.lng === lon) {
                handleMarkerNavigation(m)
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

function navigateHome() {
    if (window.location.hash) {
        window.history.pushState(null, null, ' ')
    }
    navigate() // clears rest
}

// Export functions to window object
window.navigate = navigate;
window.navigateHome = navigateHome;

// Set up hash change listener
window.onhashchange = navigate

// Initial navigation
navigate()

// Handle special hash states (success, duplicate, failed, registered)
// Keep this after the initial navigation to prevent the messages from being cleared immediately
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

document.querySelector('#export-gpx').onclick = exportAsGPX
