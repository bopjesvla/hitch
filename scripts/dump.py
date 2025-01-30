import os
import sqlite3

import pandas as pd

root_dir = os.path.join(os.path.dirname(__file__), "..")
db_dir = os.path.abspath(os.path.join(root_dir, "db"))
dist_dir = os.path.abspath(os.path.join(root_dir, "dist"))

os.makedirs(dist_dir, exist_ok=True)

DATABASE = os.path.join(db_dir, "prod-points.sqlite")
DATABASE_DUMP = os.path.join(dist_dir, "dump.sqlite")
EXCEL_DUMP = os.path.join(dist_dir, "dump.xlsx")

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

with pd.ExcelWriter(EXCEL_DUMP) as writer:
    all_points.to_excel(writer, sheet_name="points")  
    duplicates.to_excel(writer, sheet_name="duplicates")  