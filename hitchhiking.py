from string import Template

from datasets import load_dataset
import folium
from heatchmap.gpmap import GPMap
from heatchmap.map_based_model import BUCKETS, BOUNDARIES
import matplotlib.colors as colors
import numpy as np
import xyzservices.providers as xyz


tiles = xyz.CartoDB.Positron

m = folium.Map(
    tiles=folium.TileLayer(no_wrap=True, tiles=tiles),
    attr="Heatchmap",
    min_zoom=1,
)


cmap = colors.ListedColormap(BUCKETS)

norm = colors.BoundaryNorm(BOUNDARIES, cmap.N, clip=True)
cmap.set_bad(color="#000000", alpha=0.0) # opaque for NaN values (sea)
ds = load_dataset("tillwenke/heatchmap-map", cache_dir="cache/huggingface")
ds = ds.with_format("np")
image = ds["train"]["numpy"]

mymap = GPMap()
mymap.get_map_grid()
mymap.get_landmass_raster()

image = np.where(mymap.landmass_raster, image, np.nan)
image = norm(image).data

# Input 2D scalar array
scalars = image

# Apply the colormap to scalars
colors = cmap(scalars)

# Combine RGB values with the opacity
rgba_array = np.empty_like(colors)
rgba_array[:, :, :3] = colors[:, :, :3]  # RGB
# TODO: get with uncertainty
rgba_array[:, :, 3] = 1.0  # A


folium.raster_layers.ImageOverlay(
    image=rgba_array,
    bounds=[[-56, -180], [80, 180]],
).add_to(m)


# from show.py

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

outname = "hitchhiking.html"
template = open("src.html", encoding="utf-8").read()

output = Template(template).substitute(
    {
        "folium_head": header,
        "folium_body": body,
        "folium_script": script,
        "hitch_script": open("map.js", encoding="utf-8").read(),
        "hitch_style": open("style.css", encoding="utf-8").read(),
    }
)

open(outname, "w", encoding="utf-8").write(output)
print(f"Map saved to {outname}")
print("Done.")