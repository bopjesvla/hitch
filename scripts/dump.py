import os
import sqlite3

import pandas as pd
from helpers import get_dirs

from db import DATABASE_URI as DATABASE

scripts_dir, root_dir, base_dir, db_dir, dist_dir, *dirs = get_dirs()

os.makedirs(dist_dir, exist_ok=True)

DATABASE_DUMP = os.path.join(dist_dir, "dump.sqlite")

if not os.path.exists(DATABASE):
    print(f"DB not found: {DATABASE}")
    exit()

all_points = pd.read_sql(
    "select * from points where not banned", sqlite3.connect(DATABASE)
)
all_points["ip"] = ""
all_points.to_sql(
    "points", sqlite3.connect(DATABASE_DUMP), index=False, if_exists="replace"
)


duplicates = pd.read_sql(
    "select * from duplicates where reviewed = accepted", sqlite3.connect(DATABASE)
)
duplicates["ip"] = ""
duplicates.to_sql(
    "duplicates", sqlite3.connect(DATABASE_DUMP), index=False, if_exists="replace"
)
