from typing import List
from dataclasses import dataclass
from datetime import datetime
from extensions import db

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
  
  
class Review(db.Model):
  __tablename__ = "Reviews"
  
  ID: Mapped[int] = mapped_column(primary_key=True)
  Rating: Mapped[int] = mapped_column()
  Duration: Mapped[int] = mapped_column()
  CreatedBy: Mapped[str] = mapped_column()
  CreatedAt: Mapped[datetime] = mapped_column(default=datetime.now, index=True)
  PointId: Mapped[int] = mapped_column(ForeignKey("Points.ID"), default=None)


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
  ReviewCount: Mapped[int]
  Rating: Mapped[int]
  Duration: Mapped[int]
  
  @property
  def ReviewCount(self) -> int:
    return len(self.Reviews)

  @property
  def Rating(self) -> int:
    return sum([r.Rating for r in self.Reviews]) / len(self.Reviews)
  
  @property
  def Duration(self) -> int:
    durations = []
    
    for r in self.Reviews:
      if r.Duration is not None:
        durations.append(r.Duration)
    
    if len(durations) == 0:
      return None
    
    return sum(durations) / len(durations)
  
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