import pandas as pd
import sqlite3
import os

DUMP_DB = 'dump.sqlite'

fn = 'prod-points.sqlite'
if not os.path.exists(fn):
    exit()

all_points = pd.read_sql('select * from points where not banned', sqlite3.connect(fn))
all_points["ip"] = ""
all_points.to_sql('points', sqlite3.connect(DUMP_DB), index=False, if_exists='replace')

duplicates = pd.read_sql('select * from duplicates where reviewed = accepted', sqlite3.connect(fn))
duplicates["ip"] = ""
duplicates.to_sql('duplicates', sqlite3.connect(DUMP_DB), index=False, if_exists='replace')
