from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from flask_compress import Compress
from flask_caching import Cache
from flask_cors import CORS

class Base(DeclarativeBase, MappedAsDataclass):
  pass

db = SQLAlchemy(model_class=Base)
compress = Compress()
cache = Cache()
cors = CORS()