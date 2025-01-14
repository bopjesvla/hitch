import os
import sqlite3

import pandas as pd


rootDir = os.path.join(os.path.dirname(__file__), "..")

dbDir = os.path.abspath(os.path.join(rootDir, "db"))
DATABASE = os.path.join(dbDir, "prod-points.sqlite")

if not os.path.exists(DATABASE):
    exit()

all_points = pd.read_sql(
    "select * from points where not banned", sqlite3.connect(DATABASE)
)
all_points["ip"] = ""
all_points.to_sql(
    "points", sqlite3.connect("dump.sqlite"), index=False, if_exists="replace"
)


duplicates = pd.read_sql(
    "select * from duplicates where reviewed = accepted", sqlite3.connect(DATABASE)
)
duplicates["ip"] = ""
duplicates.to_sql(
    "duplicates", sqlite3.connect("dump.sqlite"), index=False, if_exists="replace"
)


hitchwiki = pd.read_sql("select * from hitchwiki", sqlite3.connect(DATABASE))
hitchwiki["ip"] = ""
hitchwiki.to_sql(
    "hitchwiki", sqlite3.connect("dump.sqlite"), index=False, if_exists="replace"
)
