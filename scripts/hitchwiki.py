import json
import os
import sqlite3
from html import unescape

import numpy as np
import pandas as pd

rootDir = os.path.join(os.path.dirname(__file__), "..")
dbDir = os.path.abspath(os.path.join(rootDir, "db"))

DATABASE = os.path.join(dbDir, "points.sqlite")


to_df = lambda x: pd.DataFrame(x.tolist(), index=x.index)

if not os.path.exists("good.json"):
    print("File missing: good.json")
    exit()

good = pd.read_json("good.json")[0]
good = good.str.split("\n").str[-1]

df = pd.DataFrame(good.apply(json.loads).tolist())

df = df[df.rating != "0"]
df["country"] = df.location.apply(lambda x: x["country"]["iso"])
df["wait"] = df.waiting_stats.apply(lambda x: x["avg"] if x else None).astype(float)
df = df.assign(**to_df(df.user.dropna()))
df["spot_datetime"] = df.datetime
df["spot_name"] = df.name

# df.loc[df.comments_count==0, 'comments'] = None

explode_df = df.explode("comments").reset_index()

# explode_df.assign(**explode_df.comments.dropna().apply(pd.Series))

explode_df = explode_df.assign(**to_df(explode_df.comments.dropna()))
explode_df = explode_df.assign(**to_df(explode_df.user.dropna()))
# comment_df.datetime = pd.to_datetime(comment_df.datetime)
explode_df[["lat", "lon", "rating"]] = explode_df[["lat", "lon", "rating"]].astype(
    float
)
explode_df.rating = 6 - explode_df.rating
explode_df.comment = explode_df.comment.dropna().apply(unescape)

explode_df.loc[explode_df.comment.isnull(), "datetime"] = explode_df.spot_datetime
explode_df.loc[explode_df.comment.isnull(), "name"] = explode_df.spot_name
explode_df.name = explode_df.name + " (Hitchwiki)"

explode_df.datetime += ".000000"

explode_df["reviewed"] = True
explode_df["banned"] = explode_df.comment.isin(
    [
        "Got a ride from the Pope of Dope.",
        "Whoever added this spot is genius xD",
        "After 4 hours a camel finally picked me up, he was very friendly.",
    ]
)
explode_df["ip"] = None
explode_df["dest_lat"] = explode_df["dest_lon"] = np.nan
# so sqlite understands they are floats
explode_df.loc[
    explode_df.comment
    == "Got a ride after 10 minutes withhout even bothering straight to Lure close to Switzerland which was where I needed to go. Lovely",
    ["dest_lat", "dest_lon"],
] = [47.6864, 6.4943]

cols = [
    "lat",
    "lon",
    "rating",
    "country",
    "wait",
    "name",
    "comment",
    "datetime",
    "reviewed",
    "banned",
    "ip",
    "dest_lat",
    "dest_lon",
]

explode_df[cols].to_sql(
    "points", sqlite3.connect(DATABASE), index_label="id", if_exists="replace"
)

# create unique index unique_comment on points(lat, lon, comment) where comment is not null;
