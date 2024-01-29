from flask import Flask
from flask import send_file, request, redirect
from flask import g
import pandas as pd
import datetime
import sqlite3
import random
import os
from hitchmap_types import HitchhikeSpot, HITCH_SPOT_INDEX

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

@app.route("/heatmap.html", methods=['GET'])
def heatmap():
    return send_file("heatmap.html")

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
    data = request.form.to_dict()

    data['id'] = random.randint(0,2**63)

    data['datetime'] = str(datetime.datetime.utcnow())

    if request.headers.getlist("X-Real-IP"):
        data['ip'] = request.headers.getlist("X-Real-IP")[-1]
    else:
        data['ip'] = request.remote_addr

    lat, lon, dest_lat, dest_lon = map(float, data['coords'].split(','))

    data['lat'] = lat
    data['lon'] = lon
    data['dest_lat'] = dest_lat
    data['dest_lon'] = dest_lon
    data['country'] = (lat, lon)

    data['reviewed'] = False
    data['banned'] = False

    hitch_spot = HitchhikeSpot(**data)
    hitch_spot_df = pd.DataFrame(hitch_spot.model_dump(), index=[0]).set_index(HITCH_SPOT_INDEX)
    hitch_spot_df.to_sql('points', get_db(), index_label=HITCH_SPOT_INDEX, if_exists='append')

    return redirect('/#success')

if __name__ == "__main__":
    app.run(debug=True)
