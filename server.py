from flask import Flask, redirect, g, render_template_string, jsonify, render_template
from flask import send_file, request, redirect
import re
import pandas as pd
import requests
import sqlite3
import random
import os
import math
from flask_sqlalchemy import SQLAlchemy
from flask_security import (
    Security,
    SQLAlchemyUserDatastore,
    current_user,
    RegisterForm,
)
from flask_security.models import fsqla_v3 as fsqla
from wtforms import IntegerField, SelectField, StringField
from wtforms.widgets import NumberInput
from wtforms.validators import Optional
from datetime import datetime
import pycountry

EMAIL = "info@hitchmap.com"

DATABASE = (
    "prod-points.sqlite" if os.path.exists("prod-points.sqlite") else "points.sqlite"
)


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


# Create app
app = Flask(__name__)

### Define user management ###

app.config["DEBUG"] = True
# generated using: secrets.token_urlsafe()
app.config["SECRET_KEY"] = (
    "pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw"  # TODO from environ
)
app.config["SECURITY_PASSWORD_HASH"] = "argon2"
# argon2 uses double hashing by default - so provide key.
# For python3: secrets.SystemRandom().getrandbits(128)
app.config["SECURITY_PASSWORD_SALT"] = (
    "146585145368132386173505678016728509634"  # TODO from environ
)

# Allow registration of new users without confirmation
app.config["SECURITY_REGISTERABLE"] = True
app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
app.config["SECURITY_CONFIRMABLE"] = False

app.config["SECURITY_USERNAME_ENABLE"] = True
app.config["SECURITY_USERNAME_REQUIRED"] = True
app.config["SECURITY_USERNAME_MIN_LENGTH"] = 1
app.config["SECURITY_USERNAME_MAX_LENGTH"] = 32
app.config["SECURITY_MSG_USERNAME_ALREADY_ASSOCIATED"] = (
    f"%(username)s is already associated with an account. Please reach out to {EMAIL} if you want to claim this username because you used it before as a nickname on hitchmap.com and/ or you use this username on hitchwiki.org as well.",
    "error",
)

# Lax = CSRF protection for POST requests, Strict would also include GET requests
app.config["SESSION_COOKIE_SAMESITE"] = 'Lax'

app.config["SECURITY_POST_REGISTER_VIEW"] = "/login"

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///../{DATABASE}"  # relative to /instance directory
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SECURITY_CHANGE_EMAIL"] = True

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

### Initiate user management ###

db = SQLAlchemy(app)
fsqla.FsModels.set_db_info(db)


class Role(db.Model, fsqla.FsRoleMixin):
    pass


class User(db.Model, fsqla.FsUserMixin):
    gender = db.Column(db.String(255))
    year_of_birth = db.Column(db.Integer)
    hitchhiking_since = db.Column(db.Integer)
    origin_country = db.Column(db.String(255))
    origin_city = db.Column(db.String(255))
    hitchwiki_username = db.Column(db.String(255))
    trustroots_username = db.Column(db.String(255))


class CountrySelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(CountrySelectField, self).__init__(*args, **kwargs)
        self.choices = [(None, "None")] + [
            (country.name, country.name) for country in pycountry.countries
        ]


class ExtendedRegisterForm(RegisterForm):
    gender = SelectField(
        "Gender",
        choices=[
            (None, "None"),
            ("Female", "Female"),
            ("Male", "Male"),
            ("Non-Binary", "Non-Binary"),
            ("Prefer not to say", "Prefer not to say"),
        ],
    )
    year_of_birth = IntegerField(
        "Year of Birth",
        widget=NumberInput(min=1900, max=datetime.now().year),
        validators=[Optional()],
    )
    hitchhiking_since = IntegerField(
        "Hitchhiking Since",
        widget=NumberInput(min=1900, max=datetime.now().year),
        validators=[Optional()],
    )
    origin_country = CountrySelectField("Where are you from?")
    origin_city = StringField("Which city are you from?", validators=[Optional()])
    hitchwiki_username = StringField("Hitchwiki Username", validators=[Optional()])
    trustroots_username = StringField("Trustroots Username", validators=[Optional()])


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

### One time setup for user management ###

with app.app_context():
    # create necessary sql tables
    security.datastore.db.create_all()
    # deine roles - not really needed
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
    security.datastore.db.session.commit()


### Endpoints related to user management ###


@app.route("/user", methods=["GET"])
def get_user():
    print("Received request to get user.")
    # Check if the user is logged in
    if not current_user.is_anonymous:
        return jsonify({"logged_in": True, "username": current_user.username})
    else:
        return jsonify({"logged_in": False, "username": ""})


@app.route("/delete-user", methods=["GET"])
def delete_user():
    updated_user = security.datastore.find_user(username=current_user.username)
    updated_user.gender = None
    updated_user.year_of_birth = None
    updated_user.hitchhiking_since = None
    updated_user.origin_country = None
    updated_user.origin_city = None
    updated_user.hitchwiki_username = None
    updated_user.trustroots_username = None
    security.datastore.put(updated_user)
    security.datastore.commit()
    return f"To delete your account please send an email to {EMAIL} with the subject 'Delete my account'."

def get_origin_string(user):
    origin_string = (
        (user.origin_city if user.origin_city is not None else "")
        + (", " if (user.origin_city != "" and user.origin_city is not None) else " ")
        + (user.origin_country if user.origin_country is not None else "")
    )
    return origin_string 

@app.route("/me", methods=["GET"])
def show_current_user():
    if current_user.is_anonymous:
        return "You are not logged in. <a href='/'>Back to Map</a>"

    user = current_user
    origin_string = get_origin_string(user)

    return render_template(
        "me.html",
        username=user.username,
        email=user.email,
        gender=user.gender,
        origin_string=origin_string,
        hitchwiki_username=user.hitchwiki_username,
        trustroots_username=user.trustroots_username,
        hitchhiking_since=user.hitchhiking_since,
        year_of_birth=user.year_of_birth,
    )


@app.route("/is_username_used/<username>", methods=["GET"])
def is_username_used(username):
    print(f"Received request to check if username {username} is used.")
    user = security.datastore.find_user(username=username)
    if user:
        return jsonify({"used": True})
    else:
        return jsonify({"used": False})


@app.route("/account/<username>", methods=["GET"])
def show_account(username):
    print(f"Received request to show user {username}.")
    user = security.datastore.find_user(username=username)
    if user:
        origin_string = get_origin_string(user)

        return render_template(
            "account.html",
            username=user.username,
            email=user.email,
            gender=user.gender,
            origin_string=origin_string,
            hitchwiki_username=user.hitchwiki_username,
            trustroots_username=user.trustroots_username,
            hitchhiking_since=user.hitchhiking_since,
            year_of_birth=user.year_of_birth,
        )
    else:
        result = f"User not found."


@app.route("/support", methods=["GET"])
def support():
    return f"To get support please send an email to {EMAIL}."


### App content ###


@app.route("/", methods=["GET"])
def index():
    return send_file("index.html")


@app.route("/light.html", methods=["GET"])
def light():
    light_map = "light.html"
    if os.path.exists(light_map):
        return send_file(light_map)
    else:
        return "No light map available."


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


### App functionality ###


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


@app.route("/content/<path:path>")
def send_report(path):
    return send_from_directory("content", path)


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

    # do not submit review if nickname is taken
    if security.datastore.find_user(username=nickname):
        return redirect("/#failed")

    signal = data["signal"] if data["signal"] != "null" else None
    assert signal in ["thumb", "sign", "ask", "ask-sign", None]

    datetime_ride = data["datetime_ride"]

    now = str(datetime.utcnow())

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
                "email": EMAIL,
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
