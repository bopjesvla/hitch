import pandas as pd
import sqlite3
import os

fn = 'prod-points.sqlite'
if not os.path.exists(fn):
    exit()
all_points = pd.read_sql('select * from points where not banned', sqlite3.connect(fn))
all_points['ip'] = ''
all_points.to_sql('points', sqlite3.connect('dump.sqlite'), index=False, if_exists='replace')

duplicates = pd.read_sql('select * from duplicates where reviewed = accepted', sqlite3.connect(fn))
duplicates['ip'] = ''
duplicates.to_sql('duplicates', sqlite3.connect('dump.sqlite'), index=False, if_exists='replace')

hitchwiki = pd.read_sql('select * from hitchwiki', sqlite3.connect(fn))
hitchwiki['ip'] = ''
hitchwiki.to_sql('hitchwiki', sqlite3.connect('dump.sqlite'), index=False, if_exists='replace')