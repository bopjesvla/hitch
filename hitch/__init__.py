import os

from flask import Flask, send_file, send_from_directory
from flask_security import SQLAlchemyUserDatastore

from hitch.blueprints.main import main_bp
from hitch.blueprints.user import user_bp
from hitch.extensions import db, mail, security
from hitch.models import Role, User
from hitch.settings import config

baseDir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_CONFIG", "development")

    app = Flask(__name__, static_url_path="", static_folder="static")
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    register_routes(app)

    return app


def register_extensions(app):
    db.init_app(app)
    mail.init_app(app)

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore)


def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp)


def register_commands(app):
    @app.cli.command()
    def init():
        """Initialize the database."""
        # create necessary sql tables
        security.datastore.db.create_all()

        # define roles - not really needed
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


def register_routes(app):
    # Serve index.html (when no path is provided; default path is not supported by dist route)
    @app.route("/")
    def index():
        return send_file(os.path.join(baseDir, "dist", "index.html"))

    # Serve dist files
    @app.route("/<path:path>")
    def dist(path="index.html"):
        return send_from_directory(os.path.join(baseDir, "dist"), path)
