import pandas as pd
import numpy as np
import folium
import json
import folium.plugins
import sqlite3
from html import unescape
import os
import datetime

fn = "hw.sqlite"
desc = pd.read_sql(
    "select p.*, waitingtime wait, null name, pd.description comment from t_points p join t_points_descriptions pd where p.id = pd.fk_point",
    sqlite3.connect(fn),
)

desc = desc.drop_duplicates("id")
desc = desc[
    ["id", "lat", "lon", "rating", "country", "wait", "nickname", "comment", "datetime"]
]
desc["datetime"] += ".000000"
desc["id"] += 1000000
desc[["lat", "lon", "rating"]] = desc[["lat", "lon", "rating"]].astype(float)
desc.rating = 6 - desc.rating
desc.comment = desc.comment.dropna().apply(unescape)

desc["reviewed"] = True
desc["banned"] = False
desc["ip"] = None
desc["dest_lat"] = desc["dest_lon"] = np.nan

desc.to_sql("points", sqlite3.connect("points.sqlite"), index=False, if_exists="append")
