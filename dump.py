import pandas as pd
import sqlite3
import os

DUMP_DB = 'dump.sqlite'

fn = 'prod-points.sqlite'
if not os.path.exists(fn):
    exit()

all_points = pd.read_sql('select * from points where not banned', sqlite3.connect(fn))
all_points.drop(columns=["ip"], inplace=True)
all_points.to_sql('points', sqlite3.connect(DUMP_DB), index=False, if_exists='replace')

duplicates = pd.read_sql('select * from duplicates where reviewed = accepted', sqlite3.connect(fn))
duplicates.drop(columns=["ip"], inplace=True)
duplicates.to_sql('duplicates', sqlite3.connect(DUMP_DB), index=False, if_exists='replace')

hitchwiki = pd.read_sql('select * from hitchwiki', sqlite3.connect(fn))
hitchwiki.drop(columns=["ip"], inplace=True)
hitchwiki.to_sql('hitchwiki', sqlite3.connect(DUMP_DB), index=False, if_exists='replace')

users = pd.read_sql('select * from user', sqlite3.connect(fn))
users = users[["id", "username", "gender", "year_of_birth"]]
users.rename(columns={"id":"user_id"}, inplace=True)
users.to_sql('user', sqlite3.connect(DUMP_DB), index=False, if_exists='replace')