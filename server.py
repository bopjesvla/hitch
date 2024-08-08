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

DATABASE = (
    "prod-points.sqlite" if os.path.exists("prod-points.sqlite") else "points.sqlite"
)

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return send_file("index.html")


@app.route("/light.html", methods=["GET"])
def light():
    return send_file("light.html")


@app.route("/lines.html", methods=["GET"])
def lines():
    return send_file("lines.html")


@app.route("/heatmap.html", methods=["GET"])
def heatmap():
    return send_file("heatmap.html")


@app.route("/tiny-world-map.json", methods=["GET"])
def tinyworldmap():
    return send_file("tiny-world-map.json")


@app.route("/heatmap-wait.html", methods=["GET"])
def heatmapwait():
    return send_file("heatmap-wait.html")


@app.route("/heatmap-distance.html", methods=["GET"])
def heatmapdistance():
    return send_file("heatmap-distance.html")


@app.route("/new.html", methods=["GET"])
def new():
    return send_file("new.html")


@app.route("/recent.html", methods=["GET"])
def recent():
    return send_file("recent.html")


@app.route("/recent-dups.html", methods=["GET"])
def recent_dups():
    return send_file("recent-dups.html")


@app.route("/favicon.ico", methods=["GET"])
def favicon():
    return send_file("favicon.ico")


@app.route("/icon.png", methods=["GET"])
def icon():
    return send_file("hitchwiki-high-contrast-no-car-flipped.png")

@app.route("/content/report_duplicate.png", methods=["GET"])
def report_duplicate_image():
    return send_file("content/report_duplicate.png")

@app.route("/content/route_planner.png", methods=["GET"])
def route_planner_image():
    return send_file("content/route_planner.png")


@app.route("/manifest.json", methods=["GET"])
def manifest():
    return send_file("manifest.json")


@app.route("/sw.js", methods=["GET"])
def sw():
    return send_file("sw.js")


@app.route("/.well-known/assetlinks.json", methods=["GET"])
def assetlinks():
    return send_file("android/assetlinks.json")


@app.route("/Hitchmap.apk", methods=["GET"])
def android_app():
    return send_file("android/Hitchmap.apk")


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
                "lat": lat, "lon": lon, "format": "json",
                "zoom": 3, "email": "info@hitchmap.com"
            }
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
            }
        ],
        index=[pid],
    )
    # , 'males': males, 'females': females, 'others': others

    df.to_sql("points", get_db(), index_label="id", if_exists="append")

    return redirect("/#success")


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
