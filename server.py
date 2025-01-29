import datetime
import logging
import math
import os
import random
import re
import secrets
import sqlite3
from datetime import datetime

import pandas as pd
import pycountry
import requests
from flask import Flask, g, jsonify, redirect, render_template, request, send_file, send_from_directory
from flask_mailman import Mail
from flask_security import Security, SQLAlchemyUserDatastore, current_user, utils
from flask_security.models import fsqla_v3 as fsqla
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import Optional
from wtforms.widgets import NumberInput

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EMAIL = "info@hitchmap.com"


root_dir = os.path.dirname(__file__)


db_dir = os.path.abspath(os.path.join(root_dir, "db"))
dist_dir = os.path.abspath(os.path.join(root_dir, "dist"))
static_dir = os.path.abspath(os.path.join(root_dir, "static"))

# TODO: Use dotenv?
if os.path.exists(os.path.join(db_dir, "prod-points.sqlite")):
    DATABASE = os.path.join(db_dir, "prod-points.sqlite")
else:
    DATABASE = os.path.join(db_dir, "points.sqlite")

# generated using: secrets.token_urlsafe()
SECRET_KEY_FILE = ".flask_secret_key"


def get_or_create_secret_key():
    # Check if the secret key file already exists
    if os.path.exists(SECRET_KEY_FILE):
        # Read the key from the file
        with open(SECRET_KEY_FILE, "r") as file:
            secret_key = file.read().strip()
    else:
        # Generate a new random secret key
        secret_key = secrets.token_hex(32)
        # Write the key to the file
        with open(SECRET_KEY_FILE, "w") as file:
            file.write(secret_key)
        logger.info(f"Generated new SECRET_KEY and saved to {SECRET_KEY_FILE}")
    return secret_key


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


app = Flask(__name__)

### Define user management ###

app.config["DEBUG"] = DATABASE == "prod-points.sqlite"

# Retrieve the secret key, creating it if necessary
app.config["SECRET_KEY"] = get_or_create_secret_key()
app.config["SECURITY_PASSWORD_HASH"] = "argon2"
app.config["SECURITY_PASSWORD_SALT"] = "146585145368132386173505678016728509634"  # can be published

# Allow registration of new users without confirmation
app.config["SECURITY_REGISTERABLE"] = True
app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
app.config["SECURITY_CONFIRMABLE"] = False
app.config["SECURITY_RECOVERABLE"] = True

app.config["SECURITY_USERNAME_ENABLE"] = True
app.config["SECURITY_USERNAME_REQUIRED"] = True
app.config["SECURITY_USERNAME_MIN_LENGTH"] = 3
app.config["SECURITY_USERNAME_MAX_LENGTH"] = 32
app.config["SECURITY_USER_IDENTITY_ATTRIBUTES"] = [{"username": {"mapper": utils.uia_username_mapper, "case_insensitive": True}}]
app.config["SECURITY_MSG_USERNAME_ALREADY_ASSOCIATED"] = (
    f"%(username)s is already associated with an account. Please reach out to {EMAIL} if you want to claim this username because you used it before as a nickname on hitchmap.com and/ or you use this username on hitchwiki.org as well.",
    "error",
)

# Lax = CSRF protection for POST requests, Strict also includes GET requests
app.config["SESSION_COOKIE_SAMESITE"] = "Strict"

app.config["SECURITY_POST_REGISTER_VIEW"] = "/#registered"

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SECURITY_CHANGE_EMAIL"] = True

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

# Flask-Mailman configuration
app.config["MAIL_SERVER"] = "mail.smtp2go.com"
app.config["MAIL_PORT"] = 587  # or 2525 if required
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = "hitchmap.com"  # SMTP2GO username
app.config["MAIL_PASSWORD"] = os.getenv("HITCHMAP_MAIL_PASSWORD", "fake-password")  # Load password from env
app.config["MAIL_DEFAULT_SENDER"] = ("Hitchmap", "no-reply@hitchmap.com")

mail = Mail(app)

### Initiate user management ###

db = SQLAlchemy(app)
fsqla.FsModels.set_db_info(db)


class Role(db.Model, fsqla.FsRoleMixin):
    pass


class User(db.Model, fsqla.FsUserMixin):
    gender = db.Column(db.String(255), default=None)
    year_of_birth = db.Column(db.Integer, default=None)
    hitchhiking_since = db.Column(db.Integer, default=None)
    origin_country = db.Column(db.String(255), default=None)
    origin_city = db.Column(db.String(255), default=None)
    hitchwiki_username = db.Column(db.String(255), default=None)
    trustroots_username = db.Column(db.String(255), default=None)


class CountrySelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(CountrySelectField, self).__init__(*args, **kwargs)
        self.choices = [(None, "None")] + [(country.name, country.name) for country in pycountry.countries]


class UserEditForm(FlaskForm):
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
    hitchwiki_username = StringField("Hitchwiki Username", validators=[Optional()], default=None)
    trustroots_username = StringField("Trustroots Username", validators=[Optional()], default=None)
    submit = SubmitField("Submit")


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
# add UserEditForm as ExtendedRegisterForm to collect additional fields while registering
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
    security.datastore.find_or_create_role(name="monitor", permissions={"admin-read", "user-read"})
    security.datastore.find_or_create_role(name="user", permissions={"user-read", "user-write"})
    security.datastore.find_or_create_role(name="reader", permissions={"user-read"})
    security.datastore.db.session.commit()


### Endpoints related to user management ###


@app.route("/edit-user", methods=["GET", "POST"])
def form():
    if current_user.is_anonymous:
        return redirect("/login")

    form = UserEditForm()

    if form.validate_on_submit():
        updated_user = security.datastore.find_user(username=current_user.username)
        updated_user.gender = form.gender.data
        updated_user.year_of_birth = form.year_of_birth.data
        updated_user.hitchhiking_since = form.hitchhiking_since.data
        updated_user.origin_country = form.origin_country.data
        updated_user.origin_city = form.origin_city.data
        updated_user.hitchwiki_username = form.hitchwiki_username.data
        updated_user.trustroots_username = form.trustroots_username.data
        security.datastore.put(updated_user)
        security.datastore.commit()
        return redirect("/me")

    form.gender.data = current_user.gender
    form.year_of_birth.data = current_user.year_of_birth
    form.hitchhiking_since.data = current_user.hitchhiking_since
    form.origin_country.data = current_user.origin_country
    form.origin_city.data = current_user.origin_city
    form.hitchwiki_username.data = current_user.hitchwiki_username
    form.trustroots_username.data = current_user.trustroots_username

    return render_template("edit_user.html", form=form)


@app.route("/user", methods=["GET"])
def get_user():
    """Endpoint to get the currently logged in user."""
    logger.info("Received request to get user.")
    # Check if the user is logged in
    if not current_user.is_anonymous:
        return jsonify({"logged_in": True, "username": current_user.username})
    else:
        return jsonify({"logged_in": False, "username": ""})


# TODO: properly delete the user after their confirmation
@app.route("/delete-user", methods=["GET"])
def delete_user():
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
        return redirect("/login")

    user = current_user
    origin_string = get_origin_string(user)

    logger.info(user.hitchwiki_username is None)
    print(user.hitchwiki_username, type(user.hitchwiki_username))

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
    """Endpoint to check if a username is already used."""
    logger.info(f"Received request to check if username {username} is used.")
    user = security.datastore.find_user(username=username)
    if user:
        return jsonify({"used": True})
    else:
        return jsonify({"used": False})


@app.route("/account/<username>", methods=["GET"])
def show_account(username):
    logger.info(f"Received request to show user {username}.")
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
        # TODO
        result = f"User not found."


### App content ###


@app.route("/", methods=["GET"])
def index():
    print("AAAA")
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


# Fallback route for static files


@app.route("/<path:path>")
def serve_static(path):
    dist_path = os.path.join(dist_dir, path)

    if os.path.exists(dist_path):
        return send_from_directory(dist_dir, path)
    else:
        return send_from_directory(static_dir, path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
