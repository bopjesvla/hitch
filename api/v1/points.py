import os

from flask import Blueprint, Response
import pandas as pd
import sqlite3

points_bp = Blueprint('points', __name__)

DATABASE = (
    "prod-points.sqlite" if os.path.exists("prod-points.sqlite") else "points.sqlite"
)

def find_all_points():
  results = pd.read_sql(
    sql="select id,lat,lon,rating from points where not banned order by datetime is not null desc, datetime desc",
    con=sqlite3.connect(DATABASE),
  )
  return results

def find_point_by_id(point_id):
  # FIX: Check if this is properly sanitized
  results = pd.read_sql(
    sql="""
      SELECT
        id, lat, lon, rating
      FROM
        points
      WHERE
        NOT banned
        AND ID = %i
    """ % point_id,
    con=sqlite3.connect(DATABASE),
  )
  
  if len(results) is 0:
    return
  
  return results.sample(1)

@points_bp.route('/')
def index():
  points = find_all_points()
  return Response(points.to_json(orient='records'), status=200, mimetype='application/json')

@points_bp.route('/', methods=['POST'])
def create():
  # Create a point
  return Response("POST /api/v1/points", status=404, mimetype='application/json')

@points_bp.route('/<int:point_id>')
def show(point_id):
  point = find_point_by_id(point_id)

  # Fix: Proper Error Handling and consistent messages
  if point is None:
    return Response(status=404)
  
  # Return a specific point with all information
  return Response(point.to_json(), status=200, mimetype='application/json')

@points_bp.route('/<int:point_id>/review', methods=['POST'])
def create_review(point_id):
  point = find_point_by_id(point_id)
  
   # Fix: Proper Error Handling and consistent messages
  if point is None:
    return Response(status=404)
  
  # Create a review for a point
  return Response("POST /api/v1/points/" + str(point_id) + "/review", status=404, mimetype='application/json')

@points_bp.route('/<int:point_id>/duplicate', methods=['POST'])
def report_duplicate(point_id):
  point = find_point_by_id(point_id)
  
   # Fix: Proper Error Handling and consistent messages
  if point is None:
    return Response(status=404)
  
  # Report duplicate points
  return Response("POST /api/v1/points/" + str(point_id) + "/duplicate", status=404, mimetype='application/json')
