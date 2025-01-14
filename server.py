import datetime
import math
import os
import random
import re
import sqlite3

import pandas as pd
import requests
from flask import Flask, g, redirect, request, send_file


rootDir = os.path.dirname(__file__)


dbDir = os.path.abspath(os.path.join(rootDir, "db"))
distDir = os.path.abspath(os.path.join(rootDir, "dist"))

# TODO: Use dotenv?
if os.path.exists(os.path.join(dbDir, "prod-points.sqlite")):
    DATABASE = os.path.join(dbDir, "prod-points.sqlite")
else:
    DATABASE = os.path.join(dbDir, "points.sqlite")


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


app = Flask(__name__, static_url_path="")


@app.route("/", methods=["GET"])
def index():
    return send_file(os.path.join(distDir, "index.html"))


@app.route("/light.html", methods=["GET"])
def light():
    light_map = os.path.join(distDir, "light.html")
    if os.path.exists(light_map):
        return send_file(light_map)
    else:
        return "No light map available."


@app.route("/lines.html", methods=["GET"])
def lines():
    return send_file(os.path.join(distDir, "lines.html"))


@app.route("/dashboard.html", methods=["GET"])
def dashboard():
    return send_file(os.path.join(distDir, "dashboard.html"))


@app.route("/heatmap.html", methods=["GET"])
def heatmap():
    return send_file(os.path.join(distDir, "heatmap.html"))


@app.route("/tiny-world-map.json", methods=["GET"])
def tinyworldmap():
    return send_file(os.path.join(distDir, "tiny-world-map.json"))


@app.route("/heatmap-wait.html", methods=["GET"])
def heatmapwait():
    return send_file(os.path.join(distDir, "heatmap-wait.html"))


@app.route("/heatmap-distance.html", methods=["GET"])
def heatmapdistance():
    return send_file(os.path.join(distDir, "heatmap-distance.html"))


@app.route("/new.html", methods=["GET"])
def new():
    return send_file(os.path.join(distDir, "new.html"))


@app.route("/recent.html", methods=["GET"])
def recent():
    return send_file(os.path.join(distDir, "recent.html"))


@app.route("/recent-dups.html", methods=["GET"])
def recent_dups():
    return send_file(os.path.join(distDir, "recent-dups.html"))


@app.route("/.well-known/assetlinks.json", methods=["GET"])
def assetlinks():
    return send_file("android/assetlinks.json")


@app.route("/Hitchmap.apk", methods=["GET"])
def android_app():
    return send_file("android/Hitchmap.apk")


# TODO: Fix SQL
@app.route("/experience", methods=["POST"])
def experience():
    data = request.form
    rating = int(data["rate"])
    wait = int(data["wait"]) if data["wait"] != "" else None
    assert wait is None or wait >= 0
    assert rating in range(1, 6)
    comment = None if data["comment"] == "" else data["comment"]
    assert comment is None or len(comment) < 10000
    name = data["username"] if re.match(r"^\w{1,32}$", data["username"]) else None

    signal = data["signal"] if data["signal"] != "null" else None
    assert signal in ["thumb", "sign", "ask", "ask-sign", None]

    datetime_ride = data["datetime_ride"]

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

    lat, lon, dest_lat, dest_lon = map(float, data["coords"].split(","))

    assert -90 <= lat <= 90
    assert -180 <= lon <= 180
    assert (-90 <= dest_lat <= 90 and -180 <= dest_lon <= 180) or (
        math.isnan(dest_lat) and math.isnan(dest_lon)
    )

    for _i in range(10):
        resp = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            {
                "lat": lat,
                "lon": lon,
                "format": "json",
                "zoom": 3,
                "email": "info@hitchmap.com",
            },
        )
        if resp.ok:
            break
        else:
            print(resp)

    res = resp.json()
    country = "XZ" if "error" in res else res["address"]["country_code"].upper()
    pid = random.randint(0, 2**63)

    df = pd.DataFrame(
        [
            {
                "rating": rating,
                "wait": wait,
                "comment": comment,
                "name": name,
                "datetime": now,
                "ip": ip,
                "reviewed": False,
                "banned": False,
                "lat": lat,
                "dest_lat": dest_lat,
                "lon": lon,
                "dest_lon": dest_lon,
                "country": country,
                "signal": signal,
                "ride_datetime": datetime_ride,
            }
        ],
        index=[pid],
    )
    # , 'males': males, 'females': females, 'others': others

    df.to_sql("points", get_db(), index_label="id", if_exists="append")

    return redirect("/#success")


# TODO: Fix SQL
@app.route("/report-duplicate", methods=["POST"])
def report_duplicate():
    data = request.form

    now = str(datetime.datetime.utcnow())

    if request.headers.getlist("X-Real-IP"):
        ip = request.headers.getlist("X-Real-IP")[-1]
    else:
        ip = request.remote_addr

    from_lat, from_lon, to_lat, to_lon = map(float, data["report"].split(","))

    df = pd.DataFrame(
        [
            {
                "datetime": now,
                "ip": ip,
                "reviewed": False,
                "accepted": False,
                "from_lat": from_lat,
                "to_lat": to_lat,
                "from_lon": from_lon,
                "to_lon": to_lon,
            }
        ]
    )

    df.to_sql("duplicates", get_db(), index=None, if_exists="append")

    return redirect("/#success-duplicate")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
