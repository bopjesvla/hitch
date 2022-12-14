from flask import Flask
from flask import send_file, request, redirect
import re
from flask import g
import pandas as pd
import requests
import datetime
import sqlite3
import random
import os

DATABASE = 'prod-points.sqlite' if os.path.exists('prod-points.sqlite') else 'points.sqlite'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

app = Flask(__name__)

@app.route("/", methods=['GET'])
def index():
    return send_file("index.html")

@app.route("/light.html", methods=['GET'])
def light():
    return send_file("light.html")

@app.route("/experience", methods=['POST'])
def experience():
    data = request.form
    rating = int(data['rate'])
    wait = int(data['wait']) if data['wait'] != '' else None
    assert wait is None or wait >= 0
    assert rating in range(1,6)
    comment = None if data['comment'] == '' else data['comment']
    assert comment is None or len(comment) < 10000
    name = data['username'] if re.match(r'^\w{1,32}$', data['username']) else None
    now = str(datetime.datetime.utcnow())

    if request.headers.getlist("X-Real-IP"):
       ip = request.headers.getlist("X-Real-IP")[-1]
    else:
       ip = request.remote_addr

    lat, lon, dest_lat, dest_lon = map(float, data['coords'].split(','))

    assert -90 <= lat <= 90
    assert -90 <= dest_lat <= 90
    assert -180 <= lon <= 180
    assert -180 <= dest_lon <= 180

    res = requests.get('https://nominatim.openstreetmap.org/reverse', {'lat': lat, 'lon': lon, 'format': 'json', 'zoom': 3}).json()
    country = 'XZ' if 'error' in res else res['address']['country_code'].upper()
    pid = random.randint(0,2**63)

    df = pd.DataFrame([{'rating': rating, 'wait': wait, 'comment': comment, 'name': name, 'datetime': now, 'ip': ip, 'reviewed': False, 'banned': False, 'lat': lat, 'dest_lat': dest_lat, 'lon': lon, 'dest_lon': dest_lon, 'country': country}], index=[pid])

    df.to_sql('points', get_db(), index_label='id', if_exists='append')

    return redirect('/#success')

if __name__ == "__main__":
    app.run(debug=True)
