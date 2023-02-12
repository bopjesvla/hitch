if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("js/sw.js").catch(e => console.error(e));
}

var is_firefox = navigator.userAgent.toLowerCase().indexOf('firefox') > -1;
var is_android = navigator.userAgent.toLowerCase().indexOf("android") > -1;

$$ = function(e) {return document.querySelector(e)}

var map = window[$$('.folium-map').id]

// Custom Controls
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

            store.topbarVisible = true;
            store.topbarStep = 1;
            store.points = [];
            renderPoints()
        }

        return controlDiv;
    }
});

map.addControl(new AddSpotButton());

if(is_firefox && is_android) document.querySelector('.leaflet-control-geocoder').style.display = 'none';

var zoom = $$('.leaflet-control-zoom')
zoom.parentNode.appendChild(zoom)

$$('a.step2-help').onclick = _ => alert(e.target.title)

// When a point is clicked on the map
function handleMarkerClick(e, point) {
  if (store.topbarVisible) return;

  setTimeout(() => {
    store.points = [new L.LatLng(point[0], point[1])];
    store.selectedSpot = point;
    store.sidebarVisible = true;
    store.sidebarSection = 'spotDetail';
  }, 100);

  L.DomEvent.stopPropagation(e)
}

// addSpotStep
function handleReviewClick(e) {
  store.topbarVisible = true;
  store.topbarStep = 2;
  renderPoints();
}

function handleAdd(e) {
  store.points.push(map.getCenter());
  store.topbarStep = 2;
  renderPoints();
}

function handleDone(gotRide = false) {
  if (!gotRide) {
    store.points.push(store.points[0]);
  } else {
    store.points.push(map.getCenter());
  }

  var bounds = new L.LatLngBounds(store.points);
  map.fitBounds(bounds, { paddingBottomRight: [0, 400] });
  map.setZoom(map.getZoom() - 1);

  store.topbarVisible = false;

  store.sidebarVisible = true;
  store.sidebarSection = 'review';

  renderPoints();
}

function handleCancel(e) {
  store.topbarVisible = false;
  store.points = [];
  renderPoints();
}

// Reset Map on Click
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

  if (!added && store.sidebarVisible) {
    store.sidebarVisible = false;
    handleCancel();
  }

  L.DomEvent.stopPropagation(e)
});

// Renders the points when reviewing / adding
function renderPoints() {
    if (store.spotMarker) map.removeLayer(store.spotMarker);
    if (store.destMarker) map.removeLayer(store.destMarker);

    store.spotMarker = store.destMarker = null;

    if (store.points[0]) {
        store.spotMarker = L.marker(store.points[0]);
        store.spotMarker.addTo(map);
    }

    if (store.points[1]) {
        store.destMarker = L.marker(store.points[1], { color: 'red' });
        store.destMarker.addTo(map);
    }

    $$('.leaflet-overlay-pane').style.opacity = store.points.length ? 0.3 : 1
}

// Copyright Marker
var c = $$('.leaflet-control-attribution')

c.innerHTML = '&copy; Bob de Ruiter | <a href=https://github.com/bopjesvla/hitch>#</a> | <a href=/dump.sqlite>⭳</a> | ' + c.innerHTML.split(',')[0].replace('© ', '').replace('OpenStreetMap', 'OSM').replace('Leaflet', 'L') + ' and <a href=https://hitchwiki.org>HitchWiki</a>'

// Check if browser supports localStorage
function storageAvailable(type) {
  try {
    var storage = window[type],
      x = '__storage_test__';
    storage.setItem(x, x);
    storage.removeItem(x);
    return true;
  } catch(e) {
    console.warn("Your browser blocks access to " + type);
    return false;
  }
}

// RestoreViewMixin
function restoreView() {
  if (!storageAvailable('localStorage')) return false;

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
  } catch (err) {
    return false;
  }
}

// Initialize map
if (!restoreView.apply(map)) map.fitBounds([[-35, -40], [60, 40]]);
if (map.getZoom() > 13) map.setZoom(13);
