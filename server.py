import math
import os
import random
import re
from datetime import datetime
import pandas as pd
import requests
from flask import jsonify, redirect, render_template, request, send_file, send_from_directory
from flask_security import current_user

from shared import app, db, dist_dir, static_dir, EMAIL, logger
from user import init_security


@app.route("/", methods=["GET"])
def index():
    return send_file(os.path.join(dist_dir, "index.html"))


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
    nickname = data["nickname"] if re.match(r"^\w{1,32}$", data["nickname"]) else None

    if app.security.datastore.find_user(username=nickname):
        return redirect("/#failed")

    signal = data["signal"] if data["signal"] != "null" else None
    assert signal in ["thumb", "sign", "ask", "ask-sign", None]

    datetime_ride = data["datetime_ride"]
    now = str(datetime.utcnow())

    ip = request.headers.getlist("X-Real-IP")[-1] if request.headers.getlist("X-Real-IP") else request.remote_addr

    lat, lon, dest_lat, dest_lon = map(float, data["coords"].split(","))

    assert -90 <= lat <= 90
    assert -180 <= lon <= 180
    assert (-90 <= dest_lat <= 90 and -180 <= dest_lon <= 180) or (math.isnan(dest_lat) and math.isnan(dest_lon))

    for _i in range(10):
        resp = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            {
                "lat": lat,
                "lon": lon,
                "format": "json",
                "zoom": 3,
                "email": EMAIL,
            },
        )
        if resp.ok:
            break
        else:
            logger.info(resp)

    res = resp.json()
    country = "XZ" if "error" in res else res["address"]["country_code"].upper()
    pid = random.randint(0, 2**63)

    df = pd.DataFrame(
        [
            {
                "rating": rating,
                "wait": wait,
                "comment": comment,
                "nickname": nickname,
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
                "user_id": current_user.id if not current_user.is_anonymous else None,
            }
        ],
        index=[pid],
    )

    df.to_sql("points", db.engine, index_label="id", if_exists="append")
    return redirect("/#success")


@app.route("/report-duplicate", methods=["POST"])
def report_duplicate():
    data = request.form
    now = str(datetime.utcnow())

    ip = request.headers.getlist("X-Real-IP")[-1] if request.headers.getlist("X-Real-IP") else request.remote_addr

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

    df.to_sql("duplicates", db.engine, index=None, if_exists="append")
    return redirect("/#success-duplicate")


@app.route("/<path:path>")
def serve_static(path):
    dist_path = os.path.join(dist_dir, path)

    if os.path.exists(dist_path):
        return send_from_directory(dist_dir, path)
    else:
        return send_from_directory(static_dir, path)


if __name__ == "__main__":
    init_security()
    app.run(host="0.0.0.0", debug=True)
