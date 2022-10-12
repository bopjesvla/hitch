import pandas as pd
import numpy as np
import folium
import json
import folium.plugins
import sqlite3
import os

points = pd.read_sql('select * from points where not banned', sqlite3.connect('prod-points.sqlite'))
print(len(points))
points.datetime = pd.to_datetime(points.datetime)
points['text'] = points['comment'] + '\n\n―' + points['name'].fillna('Anonymous') + ', ' + points.datetime.dt.strftime('%B %Y')
groups = points.groupby(['lat', 'lon'])

places = groups[['country']].first()
places['rating'] = groups.rating.mean().round()
places['rating_text'] = places.rating.replace({1: 'Terrible', 2: 'Bad', 3: 'Average', 4: 'Good', 5: 'Excellent'})
places['wait'] = points[~points.wait.isnull()].groupby(['lat', 'lon']).wait.mean()
places['text'] = 'Rating: ' + places.rating_text.fillna('-') + '\nWaiting time in minutes: ' + places.wait.fillna('-').astype(str) + '\n\n'
places.text = places.text + groups.text.apply(lambda t: '\n\n'.join(t.dropna()))

places.reset_index(inplace=True)

m = folium.Map(prefer_canvas=True)

callback = """\
function (row) {
    var marker;
    var color = {1: 'red', 2: 'orange', 3: 'yellow', 4: 'lightgreen', 5: 'lightgreen'}[row[2]];
    var opacity = {1: 0, 2: 0.4, 3: 0.6, 4: 0.8, 5: 0.8}[row[2]];
    var point = new L.LatLng(row[0], row[1])
    marker = L.circleMarker(point, {radius: 5, weight: 1 + 1 * (row[2] == 5), fillOpacity: opacity, color: 'black', fillColor: color});

    marker.on('click', function(e) {
        if ($$('#topbar').innerHTML) return
        points = [point]
        var sidebar = document.querySelector('#sidebar')
        sidebar.innerText = row[3];
        sidebar.innerHTML = `<h3>${row[0].toFixed(5)}, ${row[1].toFixed(5)}</h3><div class="comments">${sidebar.innerHTML}</div><br><button>Review this spot</button>`
        L.DomEvent.stopPropagation(e)
    })

    return marker;
};
"""

for country, group in places.groupby('country'):
    cluster = folium.plugins.FastMarkerCluster(group[['lat', 'lon', 'rating', 'text']].values, disableClusteringAtZoom=7, spiderfyOnMaxZoom=False, bubblingMouseEvents=False, callback=callback).add_to(m)

folium.plugins.Geocoder(position='topleft', add_marker=False).add_to(m)

m.fit_bounds([[-35, -40], [60, 40]])

html = m.get_root().header

html.add_child(folium.Element("""
<script>
$$ = function(e) {return document.querySelector(e)}
var points = [], spotMarker, destMarker

window.onload = function() {
    var map = window[$$('.folium-map').id]
    $$("input[placeholder^=Search]").placeholder = 'Jump to city'
    document.body.insertAdjacentHTML('beforeend',
        '<div id="sidebar"></div><a href="#" id="sb-close">&times;</a><div id="topbar">')

    $$('.leaflet-top.leaflet-left').insertAdjacentHTML('beforeend', '<div id="add-spot" class="leaflet-bar leaflet-control"><a href="#">📍 Add a spot')
    var zoom = $$('.leaflet-control-zoom')
    zoom.parentNode.appendChild(zoom)

    $$('#sb-close').onclick = function() {
        $$('#sidebar').innerHTML = ''
        points = []
        renderPoints()
    }
    $$('#add-spot').onclick = function() {
        // document.body.classList.add('picker-mode')
        $$('#topbar').innerHTML = '<span>Zoom the crosshairs into your hitchhiking spot. Be as precise as possible!</span><br><button>Done</button><button>Cancel'
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
                if(map.getZoom() > 8) map.setZoom(8);
                $$('#topbar').innerHTML = "<span>Move the crosshairs to the city/place you were dropped off.</span><br><button>Done</button><button>I didn't get a ride</button><button>Cancel"
                $$('#sidebar').innerHTML = ''
            }
            else if (points.length == 2) {
console.log(points)
                $$('#topbar').innerHTML = '';
                $$('#sidebar').innerHTML = `<h3>New Experience</h3>
                                            <p>${points[0].lat.toFixed(5)}, ${points[0].lng.toFixed(5)} → ${points[1].lat.toFixed(5)}, ${points[1].lng.toFixed(5)}</p>
                                            <form id=spot-form action=experience method=post>
                                              <input type="hidden" name="coords" value='${points[0].lat},${points[0].lng},${points[1].lat},${points[1].lng}' >
                                              <label>How do you rate the spot for your intended destination?</label>
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
        if (!$$('#sidebar form'))
            $$('#sidebar').innerHTML = ''
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
    c.innerHTML = '&copy; Bob de Ruiter | ' + c.innerHTML.split(',')[0].replace('© ', '') + ' and <a href=https://hitchwiki.org>HitchWiki</a>'
    if (window.location.hash == '#success') {
        $$('#sidebar').innerHTML = '<h3>Success!</h3>Your review will appear on the map within 10 minutes. Refreshing might be needed.'
        window.location.hash = '#'
    }
}
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
#sidebar:not(:empty) {
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    width: 400px;
    max-width: 100%;
    z-index: 999;
    background: white;
    padding: 0 20px 20px 20px;
    box-shadow: 2px 0 10px;
}
#sidebar button {
    margin-bottom: 30px;
    width: 100%;
}
#sb-close {
    display: none;
}
#sidebar:not(:empty) + #sb-close {
    display: inline-block;
    position: absolute;
    top: -10px;
    right: 0px;
    padding: 0 10px;
    cursor: pointer;
    font-size: 45px;
    z-index: 1000;
}
#add-spot {
    padding: 5px 10px;
    background: #fff !important;
    white-space: nowrap;
}
#add-spot a {
    width: auto;
}
#topbar:not(:empty) {
    pointer-events: none;
    text-align: center;
    position: absolute;
    width: 100%;
    text-shadow: 0 0 3px #fff;
    font-size: 25px;
    top: 0;
    padding: 20px;
    z-index: 1002;
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
}
#topbar:not(:empty)::before {
    content: '';
    pointer-events: none;
    position: absolute;
    left: 50vw;
    top: 50vh;
    margin-left: -30vmin;
    margin-top: -30vmin;
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
.clear::after {
    content: '';
    display: block;
    clear: both;
}
</style>
"""))

m.save('index.html')
