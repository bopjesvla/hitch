import pandas as pd
import numpy as np
import folium
import json
import folium.plugins
import sqlite3
import os
import sys
from branca.element import Element

LIGHT = 'light' in sys.argv

def haversine_np(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    All args must be of equal length.

    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2

    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c
    return km

fn = 'prod-points.sqlite' if os.path.exists('prod-points.sqlite') else 'points.sqlite'
points = pd.read_sql('select * from points where not banned', sqlite3.connect(fn))
print(len(points))

points.datetime = pd.to_datetime(points.datetime)
points['text'] = points['comment'] + '\n\n―' + points['name'].fillna('Anonymous') + ', ' + points.datetime.dt.strftime('%B %Y')

rads = points[['lat', 'lon', 'dest_lat', 'dest_lon']].values.T

points['distance'] = haversine_np(*rads)

groups = points.groupby(['lat', 'lon'])

places = groups[['country']].first()
places['rating'] = groups.rating.mean().round()
places['wait'] = points[~points.wait.isnull()].groupby(['lat', 'lon']).wait.mean()
places['distance'] = points[~points.distance.isnull()].groupby(['lat', 'lon']).distance.mean()
places['text'] = groups.text.apply(lambda t: '\n\n'.join(t.dropna()))

if LIGHT:
    places = places[(places.text.str.len() > 0) | ~places.distance.isnull()]

places['country_group'] = places.country.replace(['BE', 'NL', 'LU'], 'BNL')
places.country_group = places.country_group.replace(['CH', 'AT', 'LI'], 'ALP')
places.country_group = places.country_group.replace(['SI', 'HR', 'BA', 'ME', 'MK', 'AL', 'RS', 'TR'], 'BAL')
places.country_group = places.country_group.replace(['SK', 'HU'], 'SKHU')
places.country_group = places.country_group.replace('MC', 'FR')

places.reset_index(inplace=True)
# make sure high-rated are on top
places.sort_values('rating', inplace=True, ascending=False)

m = folium.Map(prefer_canvas=True, control_scale=True)

callback = """\
function (row) {
    var marker;
    var color = {1: 'red', 2: 'orange', 3: 'yellow', 4: 'lightgreen', 5: 'lightgreen'}[row[2]];
    var opacity = {1: 0.3, 2: 0.4, 3: 0.6, 4: 0.8, 5: 0.8}[row[2]];
    var point = new L.LatLng(row[0], row[1])
    marker = L.circleMarker(point, {radius: 5, weight: 1 + 1 * (row[2] == 5), fillOpacity: opacity, color: 'black', fillColor: color});

    marker.on('click', function(e) {
        if ($$('#topbar').innerHTML) return

        points = [point]
        var sidebar = document.querySelector('#sidebar')

        setTimeout(() => {
            sidebar.innerHTML = `<h3>${row[0].toFixed(5)}, ${row[1].toFixed(5)}</h3><div id='spot-summary'></div><h4>Comments</h4><div id='spot-text'></div><div><button>Review this spot</button></div>`
            $$('#spot-summary').innerText = `Rating: ${row[2].toFixed(0)}/5
Waiting time in minutes: ${Number.isNaN(row[4]) ? '-' : row[4].toFixed(0)}
Ride distance in km: ${Number.isNaN(row[5]) ? '-' : row[5].toFixed(0)}`

            $$('#spot-text').innerText = row[3];
            if (!row[3] && Number.isNaN(row[5])) sidebar.innerHTML += '<i>No comments/ride info. To hide points like this, check out the <a href=/light.html>lightweight map</a>.</i>'
        },100)

        L.DomEvent.stopPropagation(e)
    })

    // if(row[2] >= 4) marker.bringToFront()

    return marker;
};
"""

for country, group in places.groupby('country_group'):
    cluster = folium.plugins.FastMarkerCluster(group[['lat', 'lon', 'rating', 'text', 'wait', 'distance']].values, disableClusteringAtZoom=7, spiderfyOnMaxZoom=False, bubblingMouseEvents=False, callback=callback).add_to(m)

folium.plugins.Geocoder(position='topleft', add_marker=False).add_to(m)

m.fit_bounds([[-35, -40], [60, 40]])

html = m.get_root().header

html.add_child(folium.Element("<title>Hitchmap - Find hitchhiking spots on a map - Add new spots</title>"))

html.add_child(folium.Element("""
<script>
var is_firefox = navigator.userAgent.toLowerCase().indexOf('firefox') > -1;
var is_android = navigator.userAgent.toLowerCase().indexOf("android") > -1;

$$ = function(e) {return document.querySelector(e)}
var points = [], spotMarker, destMarker

document.addEventListener("DOMContentLoaded", function() {
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
                $$('#topbar').innerHTML = "<span>Move the crosshairs to the city/area you were dropped off when you used this spot.<sup><a href=# class=help>?</a></sup></span><br><button>Done</button><button>I didn't get a ride</button><button>Cancel"
                $$('#sidebar').innerHTML = ''
                $$('a.help').onclick = _ => alert('This is mostly used for distance and direction statistics, so it does not have to precise. If you were dropped off at multiple locations when using this spot, either choose something in the middle or leave multiple reviews.')
            }
            else if (points.length == 2) {
                var bounds = new L.LatLngBounds(points);
                map.fitBounds(bounds, {paddingBottomRight: [0, 400]})
                // if(map.getZoom() > 13) map.setZoom(13);
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
    c.innerHTML = '&copy; Bob de Ruiter | <a href=/dump.sqlite>⭳</a> | ' + c.innerHTML.split(',')[0].replace('© ', '').replace('OpenStreetMap', 'OSM') + ' and <a href=https://hitchwiki.org>HitchWiki</a>'
    if (window.location.hash == '#success') {
        $$('#sidebar').innerHTML = '<h3>Success!</h3>Your review will appear on the map within 10 minutes. Refreshing may be needed.'
        window.location.hash = '#'
    }
})
</script>
"""))
html.add_child(folium.Element("""
<style>
h3 {
    text-align: center;
    padding-bottom: 20px;
    border-bottom: 1px #eee solid;
    margin-bottom: 20px !important;
}
h3, h4 {
    font-weight: bold !important;
    font-size: 1em !important;
}
#sidebar {
    line-height: 1.5;
    font-size: 16px;
    color: #1a1a1a;
    background-color: #fdfdfd;
    hyphens: auto;
    overflow-wrap: break-word;
    text-rendering: optimizeLegibility;
    font-kerning: normal;
    overflow-y: auto;
}
#topbar:empty, #sidebar:empty {
    display: none;
}
#sidebar:not(:empty) {
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    width: 400px;
    max-width: 100%;
    z-index: 1999;
    background: white;
    padding: 0 20px 20px 20px;
    box-shadow: 2px 0 10px;
}
#sidebar button {
    margin-top: 15px;
    margin-bottom: 30px;
    width: 100%;
}
#sb-close {
    display: none;
}
#sidebar:not(:empty) + #sb-close {
    display: inline-block;
    position: absolute;
    top: -13px;
    right: 0px;
    padding: 0 10px;
    cursor: pointer;
    font-size: 45px;
    z-index: 2000;
}
.add-spot {
    padding: 5px 10px;
    background: #fff !important;
    white-space: nowrap;
}
.add-spot a {
    width: auto !important;
}
#topbar:not(:empty) {
    pointer-events: none;
    text-align: center;
    position: absolute;
    width: 100%;
    text-shadow: 0 0 3px #fff;
    font-size: 25px;
    bottom: 0;
    padding: 20px;
    z-index: 2002;
    text-shadow: 0 0 2px #fff;
}
#topbar span {
    background: rgba(255,255,255,1);
    display: inline-block;
    margin-bottom: 5px;
}
#topbar button {
    pointer-events: auto;
    width: 220px;
    max-width: 30%;
}
#topbar a {
    pointer-events: auto;
}
#topbar:not(:empty)::before {
    content: '';
    pointer-events: none;
    position: absolute;
    left: 50vw;
    bottom: 50vh;
    margin-left: -30vmin;
    margin-bottom: -30vmin;
    width: 60vmin;
    height: 60vmin;
    background: linear-gradient(to right, transparent calc(50% - 1px), rgba(255, 0, 0, .5) calc(50% - 1px), rgba(255, 0, 0, .5) calc(50% + 1px), transparent calc(50% + 1px)), linear-gradient(to bottom, transparent calc(50% - 1px), rgba(255, 0, 0, .5) calc(50% - 1px), rgba(255, 0, 0, .5) calc(50% + 1px), transparent calc(50% + 1px));
}
#spot-form > label, #spot-form textarea, #spot-form input[type=submit], #spot-form input[name=username] {
    display: block;
    width: 100%;
}
#spot-form > label, #spot-form input[type=submit] {
    margin-top: 15px;
}
.rate {
    float: left;
    height: 46px;
}
.rate:not(:checked) > input {
    position:absolute;
    top:-9999px;
}
.rate:not(:checked) > label {
    float:right;
    width:1em;
    overflow:hidden;
    white-space:nowrap;
    cursor:pointer;
    font-size:30px;
    color:#ccc;
}
.rate:not(:checked) > label:before {
    content: '★ ';
}
.rate > input:checked ~ label {
    color: #ffc700;    
}
.rate:not(:checked) > label:hover,
.rate:not(:checked) > label:hover ~ label {
    color: #deb217;  
}
.rate > input:checked + label:hover,
.rate > input:checked + label:hover ~ label,
.rate > input:checked ~ label:hover,
.rate > input:checked ~ label:hover ~ label,
.rate > label:hover ~ input:checked ~ label {
    color: #c59b08;
}
.greyed {
    background-color: #eee;
    display: inline-block;
}
.clear::after {
    content: '';
    display: block;
    clear: both;
}
@media only screen and (max-width: 700px) {
    #topbar {
        font-size: 1em !important;
    }
    #topbar button {
        font-size: 12px !important;
    }
}
</style>
"""))

outname = 'light.html' if LIGHT else 'index.html'

m.save(outname)

with open(outname) as f:
    newText=f.read().replace('</body>', '')

with open(outname, "w") as f:
    f.write(newText + '\n</body>')
