import sqlite3

import pandas as pd
from helpers import get_dirs

from db import DATABASE_URI as DATABASE

scripts_dir, root_dir, base_dir, db_dir, *dirs = get_dirs()

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
