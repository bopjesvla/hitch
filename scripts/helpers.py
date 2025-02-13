import os
import sqlite3
import numpy as np
import unicodedata
import re


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


def get_db():
    if os.path.exists(os.path.join(db_dir, "prod-points.sqlite")):
        DATABASE = os.path.join(db_dir, "prod-points.sqlite")
    else:
        DATABASE = os.path.join(db_dir, "points.sqlite")
    return sqlite3.connect(DATABASE)


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


scripts_dir = os.path.dirname(__file__)
root_dir = os.path.join(scripts_dir, "..")
db_dir = os.path.abspath(os.path.join(root_dir, "db"))
dist_dir = os.path.abspath(os.path.join(root_dir, "dist"))
