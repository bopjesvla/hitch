import os
import json

from flask import Blueprint, Response, jsonify, request
from models import Point, Review, Duplicate
from extensions import db, cache

points_bp = Blueprint('points', __name__, url_prefix='/points')

DATABASE = (
    "prod-points.sqlite" if os.path.exists("prod-points.sqlite") else "points.sqlite"
)

@points_bp.route('/')
@cache.cached(timeout=60*5, query_string=True)
def index():
  bounds = request.args.get('bounds')
  
  if bounds:
    bounds = json.loads(bounds)
    points = Point.query.filter(
      Point.Latitude.between(bounds['_southWest']['lat'], 
                             bounds['_northEast']['lat']
                             )
      ).filter(
        Point.Longitude.between(
          bounds['_southWest']['lng'],
          bounds['_northEast']['lng']
          )
        ).all()
  else:
    points = Point.query.all()
    
  return jsonify(points)

@points_bp.route('', methods=['POST'])
def create():
  data = request.json
  dataReview = data.get('Review')
  
  # TODO: Somehow, this can accept the wrong values. I don't know why.
  # An easy way to fuck up the database is by inserting a string as Review.Duration.
  point = Point(
    ID=None,
    Latitude=data.get('Latitude'),
    Longitude=data.get('Longitude'),
    Reviews=[
      Review(
        ID=None,
        PointId=None,
        Rating=dataReview.get('Rating'),
        Duration=dataReview.get('Duration'),
        Name=dataReview.get('Name'),
        Comment=dataReview.get('Comment'),
        Signal=dataReview.get('Signal'),
        RideAt=dataReview.get('RideAt'),
        CreatedBy=request.remote_addr,
      )
    ]
  )
  
  db.session.add(point)
  db.session.commit()
  
  return jsonify(point)

@points_bp.route('/<int:point_id>')
def show(point_id):
  point = Point.query.get_or_404(point_id)
  return jsonify(point)

@points_bp.route('/<int:point_id>/review', methods=['GET', 'POST'])
def create_review(point_id):
  point = Point.query.get_or_404(point_id)
  data = request.json
    
  # TODO: Somehow, this can accept the wrong values. I don't know why.
  # An easy way to fuck up the database is by inserting a string as Review.Duration.
  review = Review(
    ID=None,
    Rating=data.get('Rating'),
    Duration=data.get('Duration'),
    Name=data.get('Name'),
    Comment=data.get('Comment'),
    Signal=data.get('Signal'),
    RideAt=data.get('RideAt'),
    CreatedBy=request.remote_addr,
    PointId=point.ID
  )
  
  db.session.add(review)
  db.session.commit()
  
  return jsonify(review)

@points_bp.route('/<int:point_id>/duplicate', methods=['POST'])
def report_duplicate(point_id):
  point = Point.query.get_or_404(point_id)
  data = request.json
    
  # TODO: Somehow, this can accept the wrong values. I don't know why.
  # An easy way to fuck up the database is by inserting a string as Review.Duration.
  duplicate = Duplicate(
    ID=None,
    FromPointId=point.ID,
    ToPointId=data.get('duplicateId'),
    CreatedBy=request.remote_addr,
  )
  
  db.session.add(duplicate)
  db.session.commit()
  
  return jsonify(duplicate)
