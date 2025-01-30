# SQLite URI compatible
import os

from dotenv import load_dotenv
from helpers import get_dirs

load_dotenv()

scripts_dir, root_dir, base_dir, db_dir, *dirs = get_dirs()

DATABASE_NAME = os.getenv("DATABASE_NAME", "points.sqlite")
DATABASE_URI = os.getenv("DATABASE_URI", os.path.join(db_dir, DATABASE_NAME))
