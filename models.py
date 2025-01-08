from typing import List
from datetime import datetime
from extensions import db

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
  
class Point(db.Model):
  __tablename__ = "Points"
  
  ID: Mapped[int] = mapped_column(primary_key=True)
  Latitude: Mapped[float] = mapped_column()
  Longitude: Mapped[float] = mapped_column()
  CreatedAt: Mapped[datetime] = mapped_column(default=datetime.now(), index=True)
  Reviews: Mapped[List["Review"]] = relationship(
    default_factory=list,
    lazy="selectin"
  )
  ReviewCount: Mapped[int]
  Rating: Mapped[int]
  Duration: Mapped[int]
    
  # TODO: Surely there is a more efficient way
  @property
  def ReviewCount(self):
    return len(self.Reviews)
  
  @ReviewCount.setter
  def ReviewCount(self, value):
    pass

  # TODO: Surely there is a more efficient way
  @property
  def Rating(self):
    return round(sum([r.Rating for r in self.Reviews]) / len(self.Reviews))

  @Rating.setter
  def Rating(self, value):
    pass
  
  # TODO: Surely there is a more efficient way
  @property
  def Duration(self):
    durations = []
    
    for r in self.Reviews:
      if r.Duration is not None:
        durations.append(r.Duration)
    
    if len(durations) == 0:
      return None
    
    return round(sum(durations) / len(durations))
  
  @Duration.setter
  def Duration(self, value):
    pass

class Review(db.Model):
  __tablename__ = "Reviews"
  
  ID: Mapped[int] = mapped_column(primary_key=True)
  Rating: Mapped[int] = mapped_column()
  Duration: Mapped[int] = mapped_column()
  Name: Mapped[int] = mapped_column()
  Comment: Mapped[str] = mapped_column()
  Signal: Mapped[str] = mapped_column()
  RideAt: Mapped[str] = mapped_column()
  CreatedBy: Mapped[str] = mapped_column()
  CreatedAt: Mapped[datetime] = mapped_column(default=datetime.now(), index=True)
  PointId: Mapped[int] = mapped_column(ForeignKey("Points.ID"), default=None)