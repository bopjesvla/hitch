import html
import os
import sqlite3
import sys
from string import Template

import folium
import folium.plugins
import networkx
import numpy as np
import pandas as pd
from helpers import get_bearing, get_dirs, haversine_np

from db import DATABASE_URI as DATABASE

scripts_dir, root_dir, base_dir, db_dir, dist_dir, template_dir = get_dirs()

os.makedirs(dist_dir, exist_ok=True)

LIGHT = "light" in sys.argv
NEW = "new" in sys.argv

if LIGHT:
    outname = os.path.join(dist_dir, "light.html")
elif NEW:
    outname = os.path.join(dist_dir, "new.html")
else:
    outname = os.path.join(dist_dir, "index.html")

outname_recent = os.path.join(dist_dir, "recent.html")
outname_dups = os.path.join(dist_dir, "recent-dups.html")


template_path = os.path.join(template_dir, "index_template.html")
template = open(template_path, encoding="utf-8").read()

points = pd.read_sql(
    sql="select * from points where not banned order by datetime is not null desc, datetime desc",
    con=sqlite3.connect(DATABASE),
)

points["user_id"] = points["user_id"].astype(pd.Int64Dtype())

duplicates = pd.read_sql(
    "select * from duplicates where reviewed = accepted", sqlite3.connect(DATABASE)
)

try:
    users = pd.read_sql("select * from user", sqlite3.connect(DATABASE))
except pd.errors.DatabaseError:
    raise Exception("Run server.py to create the user table")

print(f"{len(points)} points currently")

# merging and transforming data
dup_rads = duplicates[["from_lon", "from_lat", "to_lon", "to_lat"]].values.T

duplicates["distance"] = haversine_np(*dup_rads)
duplicates["from"] = duplicates[["from_lat", "from_lon"]].apply(tuple, axis=1)
duplicates["to"] = duplicates[["to_lat", "to_lon"]].apply(tuple, axis=1)

duplicates = duplicates[duplicates.distance < 1.25]

dups = networkx.from_pandas_edgelist(duplicates, "from", "to")
islands = networkx.connected_components(dups)

replace_map = {}

for island in islands:
    parents = [node for node in island if node not in duplicates["from"].tolist()]

    if len(parents) == 1:
        for node in island:
            if node != parents[0]:
                replace_map[node] = parents[0]

print("Currently recorded duplicate spots are represented by:", dups)

points[["lat", "lon"]] = points[["lat", "lon"]].apply(
    lambda x: replace_map[tuple(x)] if tuple(x) in replace_map else x, axis=1, raw=True
)

# dups = duplicates.merge(points, left_on='child_id', right_on='id').merge(left_on='parent_id', right_on='id', suffixes=('child_', 'parent_'))

points.loc[points.id.isin(range(1000000, 1040000)), "comment"] = (
    points.loc[points.id.isin(range(1000000, 1040000)), "comment"]
    .str.encode("cp1252", errors="ignore")
    .str.decode("utf-8", errors="ignore")
)

points["datetime"] = pd.to_datetime(points.datetime)
points["ride_datetime"] = pd.to_datetime(
    points.ride_datetime, errors="coerce"
)  # handels invalid dates

rads = points[["lon", "lat", "dest_lon", "dest_lat"]].values.T

points["distance"] = haversine_np(*rads)
points["direction"] = get_bearing(*rads)

points.loc[(points.distance < 1), "dest_lat"] = None
points.loc[(points.distance < 1), "dest_lon"] = None
points.loc[(points.distance < 1), "direction"] = None
points.loc[(points.distance < 1), "distance"] = None

rounded_dir = 45 * np.round(points.direction / 45)
points["arrows"] = rounded_dir.replace(
    {
        -90: "←",
        90: "→",
        0: "↑",
        180: "↓",
        -180: "↓",
        -45: "↖",
        45: "↗",
        135: "↘",
        -135: "↙",
    }
)

rating_text = "rating: " + points.rating.astype(int).astype(str) + "/5"
destination_text = (
    ", ride: "
    + np.round(points.distance).astype(str).str.replace(".0", "", regex=False)
    + " km "
    + points.arrows
)

points["wait_text"] = None
has_accurate_wait = ~points.wait.isnull() & ~points.datetime.isnull()
points.loc[has_accurate_wait, "wait_text"] = (
    ", wait: "
    + points.wait[has_accurate_wait].astype(int).astype(str)
    + " min"
    + (
        " "
        + points.signal[has_accurate_wait].replace(
            {"ask": "💬", "ask-sign": "💬+🪧", "sign": "🪧", "thumb": "👍"}
        )
    ).fillna("")
)


def e(s):
    s2 = s.copy()
    s2.loc[~s2.isnull()] = s2.loc[~s2.isnull()].map(
        lambda x: html.escape(x).replace("\n", "<br>")
    )
    return s2


points["extra_text"] = (
    rating_text + points.wait_text.fillna("") + destination_text.fillna("")
)

comment_nl = points["comment"] + "\n\n"

# show review without comments in the sidebar if they're new; old reviews may be aggregate ratings that don't make sense
comment_nl.loc[(points.datetime.dt.year > 2021) & points.comment.isnull()] = ""

review_submit_datetime = points.datetime.dt.strftime(", %B %Y").fillna("")

points["username"] = pd.merge(
    left=points[["user_id"]],
    right=users[["id", "username"]],
    left_on="user_id",
    right_on="id",
    how="left",
)["username"]
points["hitchhiker"] = points["nickname"].fillna(points["username"])

points["user_link"] = (
    "<a href='/?user="
    + e(points["hitchhiker"])
    + "#filters'>"
    + e(points["hitchhiker"])
    + "</a>"
).fillna("Anonymous")

points["text"] = (
    e(comment_nl)
    + "<i>"
    + e(points["extra_text"])
    + "</i><br><br>―"
    + points["user_link"]
    + points.ride_datetime.dt.strftime(", %a %d %b %Y, %H:%M").fillna(
        review_submit_datetime
    )
)

oldies = points.datetime.dt.year <= 2021
points.loc[oldies, "text"] = (
    e(comment_nl[oldies])
    + "―"
    + points.loc[oldies, "user_link"]
    + points[oldies].datetime.dt.strftime(", %B %Y").fillna("")
)

# has_text = ~points.text.isnull()
# points.loc[has_text, 'text'] = points.loc[has_text, 'text'].map(lambda x: html.escape(x).replace('\n', '<br>'))

groups = points.groupby(["lat", "lon"])

places = groups[["country"]].first()
places["rating"] = groups.rating.mean().round()
places["wait"] = points[~points.wait.isnull()].groupby(["lat", "lon"]).wait.mean()
places["distance"] = (
    points[~points.distance.isnull()].groupby(["lat", "lon"]).distance.mean()
)
places["text"] = groups.text.apply(lambda t: "<hr>".join(t.dropna()))

# to prevent confusion, only add a review user if their review is listed
places["review_users"] = (
    points.dropna(subset=["text", "hitchhiker"])
    .groupby(["lat", "lon"])
    .hitchhiker.unique()
    .apply(list)
)

places["dest_lats"] = (
    points.dropna(subset=["dest_lat", "dest_lon"])
    .groupby(["lat", "lon"])
    .dest_lat.apply(list)
)
places["dest_lons"] = (
    points.dropna(subset=["dest_lat", "dest_lon"])
    .groupby(["lat", "lon"])
    .dest_lon.apply(list)
)

if LIGHT:
    places = places[(places.text.str.len() > 0) | ~places.distance.isnull()]
elif NEW:
    places = places[~places.distance.isnull()]

places.reset_index(inplace=True)
# make sure high-rated are on top
places.sort_values("rating", inplace=True, ascending=False)

m = folium.Map(prefer_canvas=True, control_scale=True, world_copy_jump=True, min_zoom=1)

callback = """\
function (row) {
    var marker;
    var color = {1: 'red', 2: 'orange', 3: 'yellow', 4: 'lightgreen', 5: 'lightgreen'}[row[2]];
    var opacity = {1: 0.3, 2: 0.4, 3: 0.6, 4: 0.8, 5: 0.8}[row[2]];
    var point = new L.LatLng(row[0], row[1])
    marker = L.circleMarker(point, {radius: 5, weight: 1 + (row[6].length > 2), fillOpacity: opacity, color: 'black', fillColor: color, _row: row});

    marker.on('click', function(e) {
       handleMarkerClick(marker, point, e)
    })

    // if 3+ reviews, whenever the marker is rendered, wait until other markers are rendered, then bring to front
    if (row[6].length >= 3) {
        marker.on('add', _ => setTimeout(_ => marker.bringToFront(), 0))
    }

    if (row[7].length) destinationMarkers.push(marker)
    allMarkers.push(marker)

    return marker;
};
"""

# for country, group in places.groupby('country_group'):
cluster = folium.plugins.FastMarkerCluster(
    places[
        [
            "lat",
            "lon",
            "rating",
            "text",
            "wait",
            "distance",
            "review_users",
            "dest_lats",
            "dest_lons",
        ]
    ].values,
    disableClusteringAtZoom=7,
    spiderfyOnMaxZoom=False,
    bubblingMouseEvents=False,
    callback=callback,
    animate=False,
).add_to(m)

# folium.plugins.Geocoder(position='topleft', add_marker=False, provider='photon').add_to(m)

m.get_root().render()

header = m.get_root().header.render()
header = header.replace(
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css"/>',
    '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css">',
)
header = header.replace(
    '<link rel="stylesheet" href="https://netdna.bootstrapcdn.com/bootstrap/3.0.0/css/bootstrap.min.css"/>',
    '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap-theme.min.css">',
)
body = m.get_root().html.render()
script = m.get_root().script.render()

# We embed everything directly into the HTML page so our service worker can't serve inconsistent files
# For example, if we add a new attribute to the spot which is shown in the front-end, but the user only gets the new
# presentation layer, not the new data, the application would break
# Because the HTML file contains everything, this is not a problem

output = Template(template).substitute(
    {
        "folium_head": header,
        "folium_body": body,
        "folium_script": script,
        "hitch_script": open(
            os.path.join(base_dir, "static", "map.js"), encoding="utf-8"
        ).read(),
        "hitch_style": open(
            os.path.join(base_dir, "static", "style.css"), encoding="utf-8"
        ).read(),
    }
)

open(outname, "w", encoding="utf-8").write(output)

if not LIGHT:
    recent = (
        points.dropna(subset=["datetime"])
        .sort_values("datetime", ascending=False)
        .iloc[:1000]
    )
    recent["url"] = (
        "https://hitchmap.com/#" + recent.lat.astype(str) + "," + recent.lon.astype(str)
    )
    recent["text"] = points.comment.fillna("") + " " + points.extra_text.fillna("")
    recent["hitchhiker"] = recent.hitchhiker.str.replace("://", "", regex=False)
    recent["distance"] = recent["distance"].round(1)
    recent["datetime"] = recent["datetime"].astype(str)
    recent["datetime"] += np.where(~recent.ride_datetime.isnull(), " 🕒", "")

    recent[
        ["url", "country", "datetime", "hitchhiker", "rating", "distance", "text"]
    ].to_html(outname_recent, render_links=True, index=False)

    duplicates["from_url"] = (
        "https://hitchmap.com/#"
        + duplicates.from_lat.astype(str)
        + ","
        + duplicates.from_lon.astype(str)
    )
    duplicates["to_url"] = (
        "https://hitchmap.com/#"
        + duplicates.to_lat.astype(str)
        + ","
        + duplicates.to_lon.astype(str)
    )
    duplicates[
        ["id", "from_url", "to_url", "distance", "reviewed", "accepted"]
    ].to_html(outname_dups, render_links=True, index=False)
