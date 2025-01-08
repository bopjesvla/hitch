from typing import List
from dataclasses import dataclass
from datetime import datetime
from extensions import db

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase, MappedAsDataclass
from sqlalchemy.ext.hybrid import hybrid_property
  
class Point(db.Model):
  __tablename__ = "Points"
  
  ID: Mapped[int] = mapped_column(primary_key=True)
  Latitude: Mapped[float] = mapped_column()
  Longitude: Mapped[float] = mapped_column()
  CreatedAt: Mapped[datetime] = mapped_column(default=datetime.now, index=True)
  Reviews: Mapped[List["Review"]] = relationship(
    default_factory=list,
    lazy="selectin"
  )
  
  @hybrid_property
  def ReviewCount(self) -> int:
    return self.Reviews.length

class Review(db.Model):
  __tablename__ = "Reviews"
  
  ID: Mapped[int] = mapped_column(primary_key=True)
  Rating: Mapped[int] = mapped_column()
  Duration: Mapped[int] = mapped_column()
  CreatedBy: Mapped[str] = mapped_column()
  CreatedAt: Mapped[datetime] = mapped_column(default=datetime.now, index=True)
  PointId: Mapped[int] = mapped_column(ForeignKey("Points.ID"), default=None)

@dataclass
class Comment(db.Model):
  __tablename__ ="Comments"
  
  ID: Mapped[int] = mapped_column(primary_key=True)
  
#   ID = db.Column(db.Integer, primary_key=True)
#   Latitude = db.Column(db.String(255))
#   Longitude = db.Column(db.String(255))
#   Distance = db.Column(db.Integer)
#   # Point = db.relationship('Point')
#   # Review = db.relationship('Review')