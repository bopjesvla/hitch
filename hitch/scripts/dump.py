import os
import sqlite3

import pandas as pd

from hitch.helpers import get_db, get_dirs

dirs = get_dirs()

os.makedirs(dirs["dist"], exist_ok=True)

DATABASE_DUMP = os.path.join(dirs["dist"], "dump.sqlite")
CSV_DUMP = os.path.join(dirs["dist"], "dump.csv")

all_points = pd.read_sql("select * from points where not banned", get_db())
all_points["ip"] = ""
all_points.to_sql("points", sqlite3.connect(DATABASE_DUMP), index=False, if_exists="replace")


duplicates = pd.read_sql("select * from duplicates where reviewed = accepted", get_db())
duplicates["ip"] = ""
duplicates.to_sql("duplicates", sqlite3.connect(DATABASE_DUMP), index=False, if_exists="replace")

all_points.to_csv(CSV_DUMP, index=False)