from flask import Flask, redirect
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

from flask_babel import Babel
from flask import Flask, render_template_string, current_app, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, auth_required, hash_password, current_user
from flask_security.models import fsqla_v3 as fsqla


DATABASE = (
    "prod-points.sqlite" if os.path.exists("prod-points.sqlite") else "points.sqlite"
)


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


# Create database connection object
db = SQLAlchemy()

# Define models
fsqla.FsModels.set_db_info(db, user_table_name="myuser", role_table_name="myrole")

class Role(db.Model, fsqla.FsRoleMixin):
    __tablename__ = "myrole"
    

class User(db.Model, fsqla.FsUserMixin):
    __tablename__ = "myuser"


# Create app
app = Flask(__name__)
app.config["DEBUG"] = True
# generated using: secrets.token_urlsafe()
app.config["SECRET_KEY"] = "pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw"
app.config["SECURITY_PASSWORD_HASH"] = "argon2"
# argon2 uses double hashing by default - so provide key.
# For python3: secrets.SystemRandom().getrandbits(128)
app.config["SECURITY_PASSWORD_SALT"] = "146585145368132386173505678016728509634"

# Take password complexity seriously
app.config["SECURITY_PASSWORD_COMPLEXITY_CHECKER"] = "zxcvbn"

# Allow registration of new users without confirmation
app.config["SECURITY_REGISTERABLE"] = True
app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
app.config["SECURITY_CONFIRMABLE"] = False

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "SQLALCHEMY_DATABASE_URI", "sqlite://"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# As of Flask-SQLAlchemy 2.4.0 it is easy to pass in options directly to the
# underlying engine. This option makes sure that DB connections from the pool
# are still valid. Important for entire application since many DBaaS options
# automatically close idle connections.
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

# Setup Flask-Security
db.init_app(app)
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
app.security = Security(app, user_datastore)

# Setup Babel - not strictly necessary but since our virtualenv has Flask-Babel
# we need to initialize it
Babel(app)


# one time setup
with app.app_context():
    if current_app.testing:
        pass
    with current_app.app_context():
        security = current_app.security
        security.datastore.db.create_all()
        security.datastore.find_or_create_role(
            name="admin",
            permissions={"admin-read", "admin-write", "user-read", "user-write"},
        )
        security.datastore.find_or_create_role(
            name="monitor", permissions={"admin-read", "user-read"}
        )
        security.datastore.find_or_create_role(
            name="user", permissions={"user-read", "user-write"}
        )
        security.datastore.find_or_create_role(name="reader", permissions={"user-read"})

        if not security.datastore.find_user(email="admin@me.com"):
            security.datastore.create_user(
                email="admin@me.com",
                password=hash_password("password"),
                roles=["admin"],
            )
        if not security.datastore.find_user(email="ops@me.com"):
            security.datastore.create_user(
                email="ops@me.com",
                password=hash_password("password"),
                roles=["monitor"],
            )
        real_user = security.datastore.find_user(email="user@me.com")
        if not real_user:
            real_user = security.datastore.create_user(
                email="user@me.com", password=hash_password("password"), roles=["user"]
            )
        if not security.datastore.find_user(email="reader@me.com"):
            security.datastore.create_user(
                email="reader@me.com",
                password=hash_password("password"),
                roles=["reader"],
            )

        security.datastore.db.session.commit()


@app.route("/", methods=["GET"])
def index():
    return send_file("index.html")


@app.route('/get_user', methods=['GET'])
def get_user():
    # Check if the user is logged in
    if current_user:  # Assuming 'user_id' is stored in session upon login
        return jsonify({'logged_in': True, 'username': current_user.id})
    else:
        return jsonify({'logged_in': False, 'username': ""})


@app.route("/light.html", methods=["GET"])
def light():
    return send_file("light.html")


@app.route("/lines.html", methods=["GET"])
def lines():
    return send_file("lines.html")


@app.route("/dashboard.html", methods=["GET"])
def dashboard():
    return send_file("dashboard.html")

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

@app.route('/content/<path:path>')
def send_report(path):
    return send_from_directory('content', path)


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
                "user_id": current_user.id
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

# @app.route('/user/<username>')
# def user_page(username):
#     user = User.query.filter_by(username=username).first_or_404()
#     reviews = pd.read_sql(f"SELECT * FROM points WHERE user_id = {user.id}", get_db())
#     return render_template('user_page.html', user=user, reviews=reviews)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
