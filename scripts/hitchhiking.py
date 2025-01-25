from string import Template

import folium
from heatchmap.gpmap import GPMap
from heatchmap.map_based_model import BUCKETS, BOUNDARIES
import matplotlib.colors as colors
import numpy as np
import xyzservices.providers as xyz
import branca.colormap as cm
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BUCKETS = BUCKETS[:-1]
BOUNDARIES = BOUNDARIES[:-1]

tiles = xyz.CartoDB.Positron
m = folium.Map(
    tiles=folium.TileLayer(no_wrap=True, tiles=tiles),
    attr="Heatchmap",
    min_zoom=1,
    max_zoom=5,
)


cmap = colors.ListedColormap(BUCKETS)

norm = colors.BoundaryNorm(BOUNDARIES, cmap.N, clip=True)
cmap.set_bad(color="#000000", alpha=0.0) # opaque for NaN values (sea)

gpmap = GPMap()
gpmap.get_map_grid()
gpmap.get_landmass_raster()

image = gpmap.raw_raster
image = np.where(gpmap.landmass_raster, image, np.nan)
image = norm(image).data
# Apply the colormap to scalars
colors = cmap(image)

uncertainties = gpmap.uncertainties
# no uncertainties for sea -> becomes fully transparent
uncertainties = np.where(
    gpmap.landmass_raster, uncertainties, uncertainties.max()
)
# Normalize uncertainties
uncertainties = (uncertainties - uncertainties.min()) / (
    uncertainties.max() - uncertainties.min()
)
uncertainties = 1 - uncertainties

# Combine RGB values with the opacity
rgba_array = np.empty_like(colors)
rgba_array[:, :, :3] = colors[:, :, :3]  # RGB
rgba_array[:, :, 3] = uncertainties

folium.raster_layers.ImageOverlay(
    image=rgba_array,
    bounds=[[-56, -180], [80, 180]],
).add_to(m)


legend = cm.LinearColormap(colors=BUCKETS, index=BOUNDARIES[:-1], vmin=BOUNDARIES[0], vmax=BOUNDARIES[-1])
legend.caption = "Waiting time to catch a ride by hitchhiking (minutes)"
m.add_child(legend)

### from show.py ###
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

root_dir = os.path.join(os.path.dirname(__file__), "..")
dist_dir = os.path.abspath(os.path.join(root_dir, "dist"))
template_dir = os.path.abspath(os.path.join(root_dir, "templates"))
outname = os.path.join(dist_dir, "hitchhiking.html")
template_dir = os.path.abspath(os.path.join(root_dir, "templates"))
template_path = os.path.join(template_dir, "index_template.html")
template = open(template_path, encoding="utf-8").read()

output = Template(template).substitute(
    {
        "folium_head": header,
        "folium_body": body,
        "folium_script": script,
        "hitch_script":  open(os.path.join(root_dir, "static", "map.js"), encoding="utf-8").read(),
        "hitch_style": open(os.path.join(root_dir, "static", "style.css"), encoding="utf-8").read()
    }
)

open(outname, "w", encoding="utf-8").write(output)
print(f"Map saved to {outname}")

### Heatmap info ###

# import matplotlib.colors as colors

# norm_uncertainties = plt.Normalize(0, 1)
# cmap_uncertainties = colors.LinearSegmentedColormap.from_list(
#     "", ["#00c800", background_color]
# )

# # from https://stackoverflow.com/a/56900830
# cax = fig.add_axes(
#     [
#         ax.get_position().x1 + 0.01,
#         ax.get_position().y0
#         + (ax.get_position().height * 2 / 3)
#         - (ax.get_position().height / 20),
#         0.02,
#         (ax.get_position().height / 3),
#     ]
# )

# cbar_uncertainty = fig.colorbar(
#     cm.ScalarMappable(norm=norm_uncertainties, cmap=cmap_uncertainties),
#     cax=cax,
# )
# cbar_uncertainty.ax.tick_params(labelsize=figsize)
# cbar_uncertainty.ax.set_ylabel(
#     "Uncertainty in waiting time estimation",
#     rotation=90,
#     fontsize=figsize * 2 / 3,
# )

# # from https://stackoverflow.com/a/56900830
# cax = fig.add_axes(
# [
#     ax.get_position().x1 + 0.01,
#     ax.get_position().y0 + (ax.get_position().height / 20),
#     0.02,
#     (ax.get_position().height / 3),
# ]
# )
# cbar = fig.colorbar(
# cm.ScalarMappable(norm=norm, cmap=cmap),
# cax=cax,
# )
# boundary_labels = [
# "0 min",
# "10",
# "20",
# "30",
# "40",
# "50",
# "60",
# "70",
# "80",
# "90",
# "> 100",
# ]
# cbar.ax.set_yticks(ticks=boundaries, labels=boundary_labels)
# cbar.ax.tick_params(labelsize=figsize)
        
logger.info("Done.")