import os
import sys

from flask_security import utils

baseDir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# SQLite URI compatible
sql_prefix = "sqlite:///" if sys.platform.startswith("win") else "sqlite:////"


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key")
    EMAIL = os.getenv("EMAIL", "info@hitchmap.com")

    # User Config
    SECURITY_PASSWORD_HASH = os.getenv("SECURITY_PASSWORD_HASH", "argon2")
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT", "146585145368132386173505678016728509634")
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_POST_REGISTER_VIEW = "/#registered"

    SECURITY_CONFIRMABLE = False
    SECURITY_RECOVERABLE = True
    SECURITY_CHANGE_EMAIL = True

    SECURITY_USERNAME_ENABLE = True
    SECURITY_USERNAME_REQUIRED = True
    SECURITY_USERNAME_MIN_LENGTH = 3
    SECURITY_USERNAME_MAX_LENGTH = 32
    SECURITY_USER_IDENTITY_ATTRIBUTES = [{"username": {"mapper": utils.uia_username_mapper, "case_insensitive": True}}]
    SECURITY_MSG_USERNAME_ALREADY_ASSOCIATED = (
        (
            "%(username)s is already associated with an account. ",
            f"Please reach out to {EMAIL} if you want to claim this username because you used it before as a nickname ",
            "on hitchmap.com and/or you use this username on hitchwiki.org as well.",
        ),
        "error",
    )

    # Lax = CSRF protection for POST requests, Strict also includes GET requests
    SESSION_COOKIE_SAMESITE = "Strict"

    # Database Config
    DATABASE_NAME = os.getenv("DATABASE_NAME", "points.sqlite")
    DATABASE_URI = os.getenv("DATABASE_URI", os.path.join(baseDir, "db", DATABASE_NAME))

    SQLALCHEMY_DATABASE_URI = sql_prefix + DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # Flask-Mailman configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER", "mail.smtp2go.com")
    MAIL_PORT = os.getenv("MAIL_PORT", 587)  # or 2525 if required
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", True)
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", False)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "hitchmap.com")  # SMTP2GO username
    MAIL_PASSWORD = os.getenv("HITCHMAP_MAIL_PASSWORD", "password")  # Load password from env
    MAIL_DEFAULT_SENDER = ("Hitchmap", "no-reply@hitchmap.com")


class DevelopmentConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    TESTING = True
    DATABASE_URI = "sqlite:///"
    WTF_CSRF_ENABLED = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
