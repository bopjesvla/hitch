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
points = pd.read_sql('select * from points where not banned order by datetime is not null desc, datetime desc', sqlite3.connect(fn))
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
places['review_count'] = groups.size()
places['dest_lats'] = points.dropna(subset=['dest_lat', 'dest_lon']).groupby(['lat', 'lon']).dest_lat.apply(list)
places['dest_lons'] = points.dropna(subset=['dest_lat', 'dest_lon']).groupby(['lat', 'lon']).dest_lon.apply(list)

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
    marker = L.circleMarker(point, {radius: 5, weight: 1 + 1 * (row[6] > 2), fillOpacity: opacity, color: 'black', fillColor: color});

    marker.on('click', function(e) {
        if ($$('.topbar.visible')) return

        points = [point]

        setTimeout(() => {
            bar('.sidebar.show-spot')
            $$('#spot-header').innerText = `${row[0].toFixed(5)}, ${row[1].toFixed(5)}`
            $$('#spot-summary').innerText = `Rating: ${row[2].toFixed(0)}/5
Waiting time in minutes: ${Number.isNaN(row[4]) ? '-' : row[4].toFixed(0)}
Ride distance in km: ${Number.isNaN(row[5]) ? '-' : row[5].toFixed(0)}`

            $$('#spot-text').innerText = row[3];
            if (!row[3] && Number.isNaN(row[5])) $$('#extra-text').innerHTML = 'No comments/ride info. To hide points like this, check out the <a href=/light.html>lightweight map</a>.'
            else $$('#extra-text').innerHTML = ''

            window.location.hash = `${row[0]},${row[1]}`
        },100)

        for (let d of destLines)
            d.remove()
        destLines = []

        if (row[7] != null) {
            for (let i in row[7]) {
                destLines.push(L.polyline([point, [row[7][i], row[8][i]]], {opacity: 0.3, dashArray: '5', color: 'black'}).addTo(map))
            }
        }

        L.DomEvent.stopPropagation(e)
    })

    if (window.location.hash == `#${row[0]},${row[1]}`)
        addEventListener("DOMContentLoaded", e => {
            marker.fire('click', {})
            map.setView(marker.getLatLng(), 16)
        });


    // if(row[2] >= 4) marker.bringToFront()

    return marker;
};
"""

for country, group in places.groupby('country_group'):
    cluster = folium.plugins.FastMarkerCluster(group[['lat', 'lon', 'rating', 'text', 'wait', 'distance', 'review_count', 'dest_lats', 'dest_lons']].values, disableClusteringAtZoom=7, spiderfyOnMaxZoom=False, bubblingMouseEvents=False, callback=callback).add_to(m)

folium.plugins.Geocoder(position='topleft', add_marker=False).add_to(m)

m.get_root().render()

header = m.get_root().header.render()
body = m.get_root().html.render()
script = m.get_root().script.render()

outname = 'light.html' if LIGHT else 'index.html'
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
    recent = points.dropna(subset=['datetime']).sort_values('datetime',ascending=False).iloc[:1000]
    recent['url'] = 'https://hitchmap.com/#' + recent.lat.astype(str) + ',' + recent.lon.astype(str)
    recent['text'] = recent.text.str.replace('://|\n|\r', '', regex=True)
    recent['name'] = recent.name.str.replace('://', '', regex=False)
    recent[['url', 'country', 'datetime', 'name', 'text']].to_html('recent.html', render_links=True, index=False)
