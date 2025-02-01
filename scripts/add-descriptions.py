import os
import sqlite3
from html import unescape

import numpy as np
import pandas as pd

root_dir = os.path.join(os.path.dirname(__file__), "..")
db_dir = os.path.abspath(os.path.join(root_dir, "db"))
dist_dir = os.path.abspath(os.path.join(root_dir, "dist"))

os.makedirs(dist_dir, exist_ok=True)

DATABASE = os.path.join(db_dir, "points.sqlite")
DATABASE_HW = os.path.join(db_dir, "hw.sqlite")

if not os.path.exists(DATABASE_HW):
    print(f"DB not found: {DATABASE_HW}")
    exit()

desc = pd.read_sql(
    "select p.*, waitingtime wait, null name, pd.description comment from t_points p join t_points_descriptions pd where p.id = pd.fk_point",  # noqa: E501
    sqlite3.connect(DATABASE_HW),
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

desc.to_sql("points", sqlite3.connect(DATABASE), index=False, if_exists="append")
