import os
import sqlite3

import pandas as pd

root_dir = os.path.join(os.path.dirname(__file__), "..")

db_dir = os.path.abspath(os.path.join(root_dir, "db"))

# TODO: Use dotenv?
if os.path.exists(os.path.join(db_dir, "prod-points.sqlite")):
    DATABASE = os.path.join(db_dir, "prod-points.sqlite")
else:
    DATABASE = os.path.join(db_dir, "points.sqlite")

################
# ensure database columns are up to date
points = pd.read_sql(
    sql="select * from points",
    con=sqlite3.connect(DATABASE),
)

points["user_id"] = pd.array([None] * len(points), dtype=pd.Int64Dtype())

if "from_hitchwiki" not in points.columns:
    points["from_hitchwiki"] = points["name"].str.contains("(Hitchwiki)")
    points["name"] = points["name"].str.replace(" (Hitchwiki)", "")

points.rename(columns={"name": "nickname"}, inplace=True)

# no links for old anonymous reviews
points.loc[points.nickname == "Anonymous", "nickname"] = None

points.to_sql("points", sqlite3.connect(DATABASE), index=False, if_exists="replace")
################
