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
import math

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

@app.route("/lines.html", methods=['GET'])
def lines():
    return send_file("lines.html")

@app.route("/heatmap.html", methods=['GET'])
def heatmap():
    return send_file("heatmap.html")

@app.route("/heatmap-wait.html", methods=['GET'])
def heatmapwait():
    return send_file("heatmap-wait.html")

@app.route("/heatmap-distance.html", methods=['GET'])
def heatmapwait():
    return send_file("heatmap-distance.html")

@app.route("/new.html", methods=['GET'])
def new():
    return send_file("new.html")

@app.route("/recent.html", methods=['GET'])
def recent():
    return send_file("recent.html")

@app.route("/favicon.ico", methods=['GET'])
def favicon():
    return send_file("favicon.ico")

@app.route("/icon.png", methods=['GET'])
def icon():
    return send_file("hitchwiki-high-contrast-no-car-flipped.png")

@app.route("/manifest.json", methods=['GET'])
def manifest():
    return send_file("manifest.json")

@app.route("/sw.js", methods=['GET'])
def sw():
    return send_file("sw.js")

@app.route("/.well-known/assetlinks.json", methods=['GET'])
def assetlinks():
    return send_file("android/assetlinks.json")

@app.route("/Hitchmap.apk", methods=['GET'])
def android_app():
    return send_file("android/Hitchmap.apk")

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

    signal = data['signal'] if data['signal'] != 'null' else None
    assert signal in ['thumb', 'sign', 'ask', 'ask-sign', None]

    # genders = [data['males'], data['females'], data['others']]
    # genders = [(int(g) if g != '' else 0) for g in genders]

    # if sum(genders) == 0:
    #     males = females = others = None
    # else:
    #     males, females, others = genders

    now = str(datetime.datetime.utcnow())

    if request.headers.getlist("X-Real-IP"):
       ip = request.headers.getlist("X-Real-IP")[-1]
    else:
       ip = request.remote_addr

    lat, lon, dest_lat, dest_lon = map(float, data['coords'].split(','))

    assert -90 <= lat <= 90
    assert -180 <= lon <= 180
    assert (-90 <= dest_lat <= 90 and -180 <= dest_lon <= 180) or (math.isnan(dest_lat) and math.isnan(dest_lon))

    res = requests.get('https://nominatim.openstreetmap.org/reverse', {'lat': lat, 'lon': lon, 'format': 'json', 'zoom': 3}).json()
    country = 'XZ' if 'error' in res else res['address']['country_code'].upper()
    pid = random.randint(0,2**63)

    df = pd.DataFrame([{'rating': rating, 'wait': wait, 'comment': comment, 'name': name, 'datetime': now, 'ip': ip, 'reviewed': False, 'banned': False, 'lat': lat, 'dest_lat': dest_lat, 'lon': lon, 'dest_lon': dest_lon, 'country': country, 'signal': signal}], index=[pid])
    # , 'males': males, 'females': females, 'others': others

    df.to_sql('points', get_db(), index_label='id', if_exists='append')

    return redirect('/#success')

if __name__ == "__main__":
    app.run(debug=True)
