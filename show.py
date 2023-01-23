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

points.loc[points.id.isin(range(1000000,1040000)), 'comment'] = points.loc[points.id.isin(range(1000000,1040000)), 'comment'].str.encode("cp1252",errors='ignore').str.decode('utf-8', errors='ignore')

points.datetime = pd.to_datetime(points.datetime)
points['text'] = points['comment'] + '\n\n―' + points['name'].fillna('Anonymous') + points.datetime.dt.strftime(', %B %Y').fillna('')

rads = points[['lon', 'lat', 'dest_lon', 'dest_lat']].values.T

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

html = m.get_root().header

html.add_child(folium.Element("<title>Hitchmap - Find hitchhiking spots on a map - Add new spots</title>"))

html.add_child(folium.Element(f"""
<script>
{open('map.js').read()}
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
