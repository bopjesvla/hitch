import os

import folium
import numpy as np
import pandas as pd
from matplotlib import cm, colors

from hitch.helpers import get_db, get_dirs, haversine_np

dirs = get_dirs()

points = pd.read_sql(
    "select * from points where not banned order by datetime is not null desc, datetime desc",
    get_db(),
)


rads = points[["lon", "lat", "dest_lon", "dest_lat"]].values.T

VAR = "distance"
DIVIDER = "wait"

points["distance"] = haversine_np(*rads, 1)

# points = points[points.datetime > '2021']
if "distance" in [VAR, DIVIDER]:
    points = points[points.distance > 0]

bin_groups = [pd.cut(points.lat, 100), pd.cut(points.lon, 100)]

stacked_grid = points.groupby(bin_groups)[VAR].mean()

if DIVIDER:
    stacked_grid /= points.groupby(bin_groups)[DIVIDER].mean()

stacked_grid_counts = points.groupby(bin_groups)[VAR].count()
stacked_grid[stacked_grid_counts < 4] = np.nan
grid = stacked_grid.unstack()
grid_counts = stacked_grid_counts.unstack()
grid = grid.iloc[::-1]
grid_counts = grid_counts.iloc[::-1]


m = folium.Map(prefer_canvas=True, control_scale=True)

# log_grid = stacked_grid.apply(lambda x: np.emath.logn(x, 2 ** .5))

for (lat, lon), g in stacked_grid.items():
    if g == g:
        if VAR == "distance" and DIVIDER == "wait":
            val = cm.RdYlGn(min(g, 5) / 5)
            tooltip = f"{round(g, 1)} km/min"
        elif VAR == "wait":
            val = cm.RdYlGn(0.9 - 0.9 * min(g, 120) / 120)
            tooltip = f"{int(g)} min"
        elif VAR == "distance":
            val = cm.RdYlGn(0.9 * min(g, 120) / 120)
            tooltip = f"{int(g)} km"
        c = colors.rgb2hex(val)
        folium.Rectangle(
            bounds=[[lat.left, lon.left], [lat.right, lon.right]],
            stroke=False,
            fill=True,
            fill_color=c,
            fill_opacity=0.3,
            tooltip=tooltip,
        ).add_to(m)

# bounds = [[grid_.index.min().left, grid_.columns.min().left],
#           [grid_.index.max().right, grid_.columns.max().right]]
# ImageOverlay(grid_counts.values, bounds, opacity=.5).add_to(m)
if DIVIDER:
    m.save(os.path.abspath(os.path.join(dirs['dist'], f"heatmap-{VAR}-per-{DIVIDER}.html")))
else:
    m.save(os.path.abspath(os.path.join(dirs['dist'], f"heatmap-{VAR}.html")))
