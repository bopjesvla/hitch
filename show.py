import pandas as pd
import numpy as np
import folium
import json
import folium.plugins
import sqlite3
import os
import sys
from branca.element import Element
from string import Template

LIGHT = 'light' in sys.argv
NEW = 'new' in sys.argv

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
    # 1.25 because the road distance is, on average, 25% larger than a straight flight
    return 1.25 * km

fn = 'prod-points.sqlite' if os.path.exists('prod-points.sqlite') else 'points.sqlite'
points = pd.read_sql('select * from points where not banned order by datetime is not null desc, datetime desc', sqlite3.connect(fn))
print(len(points))

points.loc[points.id.isin(range(1000000,1040000)), 'comment'] = points.loc[points.id.isin(range(1000000,1040000)), 'comment'].str.encode("cp1252",errors='ignore').str.decode('utf-8', errors='ignore')

points.datetime = pd.to_datetime(points.datetime)
points['text'] = points['comment'] + '\n\n―' + points['name'].fillna('Anonymous') + points.datetime.dt.strftime(', %B %Y').fillna('')

rads = points[['lon', 'lat', 'dest_lon', 'dest_lat']].values.T

points['distance'] = haversine_np(*rads)

points.loc[(points.distance<1), 'dest_lat'] = None
points.loc[(points.distance<1), 'dest_lon'] = None
points.loc[(points.distance<1), 'distance'] = None

groups = points.groupby(['lat', 'lon'])

places = groups[['country']].first()
places['rating'] = groups.rating.mean().round()
places['wait'] = points[~points.wait.isnull()].groupby(['lat', 'lon']).wait.mean()
places['distance'] = points[~points.distance.isnull()].groupby(['lat', 'lon']).distance.mean()
places['text'] = groups.text.apply(lambda t: '\n\n'.join(t.dropna()))
places['review_count'] = groups.size()
places['dest_lats'] = points.dropna(subset=['dest_lat', 'dest_lon']).groupby(['lat', 'lon']).dest_lat.apply(list)
places['dest_lons'] = points.dropna(subset=['dest_lat', 'dest_lon']).groupby(['lat', 'lon']).dest_lon.apply(list)

if LIGHT:
    places = places[(places.text.str.len() > 0) | ~places.distance.isnull()]
elif NEW:
    places = places[~places.distance.isnull()]

places.reset_index(inplace=True)
# make sure high-rated are on top
places.sort_values('rating', inplace=True, ascending=False)

m = folium.Map(prefer_canvas=True, control_scale=True, world_copy_jump=True, min_zoom=1)

# folium.map.CustomPane('back', pointer_events=False, z_index=50).add_to(m)

callback = """\
function (row) {
    var marker;
    var color = {1: 'red', 2: 'orange', 3: 'yellow', 4: 'lightgreen', 5: 'lightgreen'}[row[2]];
    var opacity = {1: 0.3, 2: 0.4, 3: 0.6, 4: 0.8, 5: 0.8}[row[2]];
    var point = new L.LatLng(row[0], row[1])
    marker = L.circleMarker(point, {radius: 5, weight: 1 + 1 * (row[6] > 2), fillOpacity: opacity, color: 'black', fillColor: color});

    marker.on('click', function(e) {
        markerClick(e, row, point)
    })

    if (window.location.hash == `#${row[0]},${row[1]}`)
        addEventListener("DOMContentLoaded", e => {
            marker.fire('click', {})
            map.setView(marker.getLatLng(), 16)
        });

    // if 3+ reviews, whenever the marker is rendered, wait until other markers are rendered, then bring to front
    if (row[6] > 2) {
        marker.on('add', _ => setTimeout(_ => marker.bringToFront(), 0))
        setTimeout(_ => marker.bringToFront(), 0)
    }

    if (window.location.pathname.includes('lines.html') && row[7] != null) {
        setTimeout(_ => {
            for (let i in row[7]) {
                L.polyline([point, [row[7][i], row[8][i]]], {opacity: 0.3, dashArray: '5', color: 'black', weight: 1}).addTo(map)
            }
        }, 0)
    }

    return marker;
};
"""

# for country, group in places.groupby('country_group'):
cluster = folium.plugins.FastMarkerCluster(places[['lat', 'lon', 'rating', 'text', 'wait', 'distance', 'review_count', 'dest_lats', 'dest_lons']].values, disableClusteringAtZoom=7, spiderfyOnMaxZoom=False, bubblingMouseEvents=False, callback=callback).add_to(m)

folium.plugins.Geocoder(position='topleft', add_marker=False).add_to(m)

m.get_root().render()

header = m.get_root().header.render()
body = m.get_root().html.render()
script = m.get_root().script.render()

outname = 'light.html' if LIGHT else 'new.html' if NEW else 'index.html'
template = open('src.html').read()

output = Template(template).substitute({
    'folium_head': header,
    'folium_body': body,
    'folium_script': script,
    'hitch_script': open('map.js').read(),
    'hitch_style': open('style.css').read()
})

open(outname, 'w').write(output)

if not LIGHT:
    open('lines.html', 'w').write(output)
    recent = points.dropna(subset=['datetime']).sort_values('datetime',ascending=False).iloc[:1000]
    recent['url'] = 'https://hitchmap.com/#' + recent.lat.astype(str) + ',' + recent.lon.astype(str)
    recent['text'] = recent.text.str.replace('://|\n|\r', '', regex=True)
    recent['name'] = recent.name.str.replace('://', '', regex=False)
    recent[['url', 'country', 'datetime', 'name', 'rating', 'distance', 'text']].to_html('recent.html', render_links=True, index=False)
