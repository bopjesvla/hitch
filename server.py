import os

from flask import Flask, redirect, g, send_file, send_from_directory, request, redirect
import re
import pandas as pd
import requests
import datetime
import sqlite3
import random
import math

from extensions import db, compress, cache, cors
from api.api import api_bp

# Database
DATABASE = (
    "prod-points.sqlite" if os.path.exists("prod-points.sqlite") else "points.sqlite"
)

def create_app():
    app = Flask(__name__)
    
    # TODO: Move into dotenv
    # SQLAlchemy
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///../{DATABASE}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = True
    
    # Cache
    app.config["CACHE_TYPE"] = "SimpleCache"
    app.config["CACHE_DEFAULT_TIMEOUT"] = 60*5
    
    # CORS
    app.config["CORS_ORIGINS"] = "*"
    
    register_extensions(app)
    register_blueprints(app)
    
    return app

def register_extensions(app):
    db.init_app(app)
    compress.init_app(app)
    cache.init_app(app)
    cors.init_app(app)
    
    def get_cache_key(request):
        return request.url
    
    compress.cache = cache
    compress.cache_key = get_cache_key
        
def register_blueprints(app):
    app.register_blueprint(api_bp)

app = create_app()

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.route("/", methods=["GET"])
def index():
    return send_file("dist/index.html")

# Vue Client
@app.route("/beta", defaults={'path': ''}, methods=["GET"])
@app.route("/beta/", defaults={'path': ''}, methods=["GET"])
@app.route("/beta/<path:path>")
def client(path):
    if (path):
        return send_from_directory('./dist_client/', path)
    return send_file('./dist_client/index.html')

@app.route("/light.html", methods=["GET"])
def light():
    return send_file("dist/light.html")


@app.route("/lines.html", methods=["GET"])
def lines():
    return send_file("dist/lines.html")


@app.route("/dashboard.html", methods=["GET"])
def dashboard():
    return send_file("dist/dashboard.html")

@app.route("/heatmap.html", methods=["GET"])
def heatmap():
    return send_file("dist/heatmap.html")


@app.route("/tiny-world-map.json", methods=["GET"])
def tinyworldmap():
    return send_file("tiny-world-map.json")


@app.route("/heatmap-wait.html", methods=["GET"])
def heatmapwait():
    return send_file("dist/heatmap-wait.html")


@app.route("/heatmap-distance.html", methods=["GET"])
def heatmapdistance():
    return send_file("dist/heatmap-distance.html")


@app.route("/new.html", methods=["GET"])
def new():
    return send_file("dist/new.html")


@app.route("/recent.html", methods=["GET"])
def recent():
    return send_file("dist/recent.html")


@app.route("/recent-dups.html", methods=["GET"])
def recent_dups():
    return send_file("dist/recent-dups.html")


@app.route("/favicon.ico", methods=["GET"])
def favicon():
    return send_file("assets/favicon.ico")


@app.route("/icon.png", methods=["GET"])
def icon():
    return send_file("assets/hitchwiki-high-contrast-no-car-flipped.png")


@app.route("/manifest.json", methods=["GET"])
def manifest():
    return send_file("assets/manifest.json")


@app.route("/sw.js", methods=["GET"])
def sw():
    return send_file("assets/sw.js")


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
