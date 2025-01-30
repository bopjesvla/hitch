import sqlite3

from flask import current_app, g


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(current_app.config["DATABASE_URI"])
    return db
