import math
import os
import random
import re
from datetime import datetime
import pandas as pd
import requests
from flask import redirect, request, send_file, send_from_directory, jsonify, render_template
from flask_security import current_user

from backend.shared import app, db, root_dir, dist_dir, static_dir, EMAIL, logger
from backend.user import init_security, security


@app.route("/", methods=["GET"])
def index():
    return send_file(os.path.join(dist_dir, "index.html"))


@app.route("/.well-known/assetlinks.json", methods=["GET"])
def assetlinks():
    return send_file(os.path.join(root_dir, "android/assetlinks.json"))


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

    if security.datastore.find_user(case_insensitive=True, username=nickname):
        return jsonify({"error": "This nickname is already used by a registered user. Please choose another nickname."}), 400

    signal = data["signal"] if data["signal"] != "null" else None
    assert signal in ["thumb", "sign", "ask", "ask-sign", None]

    datetime_ride = None if data["comment"] == "" else data["datetime_ride"]

    # this is the format used by the datetime input
    date_format = "%Y-%m-%dT%H:%M"
    assert datetime_ride is None or datetime.strptime(date_string, date_format)

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
    now = str(datetime.utcnow())

    # rate limiting
    # this might cause race conditions if the server ever runs on more than one thread
    last10seconds = pd.read_sql(
        "select * from points where ip = ? and datetime > datetime(?, '-10 seconds')", db.engine, params=(ip, now)
    )
    if len(last10seconds) > 0:
        return (
            "Rate limited. If you didn't submit multiple reviews in the last 10 seconds, your browser probably"
            + "accidentally submitted the same review twice, and it will show up shortly."
        )

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
    return jsonify({"success": True})


@app.route("/experience/<int:pid>")
def view_experience(pid):
    # Query the specific experience by id
    experience = pd.read_sql("SELECT * FROM points WHERE id = ? AND banned = False", db.engine, params=(pid,)).to_dict("records")
    print(experience)

    if not experience:
        return "Not found", 404

    experience = experience[0]

    # Convert datetime string to datetime object for formatting
    if experience["datetime"]:
        experience["datetime"] = datetime.strptime(experience["datetime"], "%Y-%m-%d %H:%M:%S.%f")
    if experience["ride_datetime"]:
        experience["ride_datetime"] = datetime.strptime(experience["ride_datetime"], "%Y-%m-%dT%H:%M")
    experience["rating"] = int(experience["rating"])
    experience["wait"] = int(experience["wait"]) if experience["wait"] else None

    # Get user info if there's a user_id
    user = None
    if experience["user_id"]:
        user = security.datastore.get_user(experience["user_id"])

    return render_template("experience.html", experience=experience, user=user)


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
