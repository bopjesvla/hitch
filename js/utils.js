// Utility functions and global variables
export function $$ (e) { return document.querySelector(e) }

export const bars = document.querySelectorAll('.sidebar, .topbar');

export function bar(selector) {
    bars.forEach(function (el) {
        el.classList.remove('visible')
    })
    if (selector)
        $$(selector).classList.add('visible')
}

export function arrowLine(from, to) {
    return L.polylineDecorator([from, to], {
        patterns: [
            {
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

export function restoreView() {
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

export function storageAvailable(type) {
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

export function summaryText(row) {
    return `Rating: ${row[2].toFixed(0)}/5
    Waiting time: ${row[4] == null ? '-' : row[4].toFixed(0) + ' min'}
    Ride distance: ${row[5] == null ? '-' : row[5].toFixed(0) + ' km'}`
}

export function closestMarker(markers, lat, lon) {
    let latlng = L.latLng(lat, lon)
    if (markers.length)
        return markers.sort((a, b) => a.getLatLng().distanceTo(latlng) - b.getLatLng().distanceTo(latlng))[0]
}
