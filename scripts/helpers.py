import os

import numpy as np


def haversine_np(lon1, lat1, lon2, lat2, factor=1.25):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    All args must be of equal length.

    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2

    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c
    # 1.25 because the road distance is, on average, 25% larger than a straight flight
    return factor * km


def get_bearing(lon1, lat1, lon2, lat2):
    dLon = lon2 - lon1
    x = np.cos(np.radians(lat2)) * np.sin(np.radians(dLon))
    y = np.cos(np.radians(lat1)) * np.sin(np.radians(lat2)) - np.sin(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.cos(
        np.radians(dLon)
    )
    brng = np.arctan2(x, y)
    brng = np.degrees(brng)

    return brng


scripts_dir = os.path.dirname(__file__)
root_dir = os.path.join(scripts_dir, "..")
db_dir = os.path.abspath(os.path.join(root_dir, "db"))
dist_dir = os.path.abspath(os.path.join(root_dir, "dist"))
