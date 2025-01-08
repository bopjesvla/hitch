from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase, MappedAsDataclass

class Base(DeclarativeBase, MappedAsDataclass):
  pass

db = SQLAlchemy(model_class=Base)