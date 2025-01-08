import os

from flask import Blueprint, Response, jsonify
from sqlalchemy import select
from sqlalchemy.orm import selectinload, noload
import pandas as pd
import sqlite3
import json

from extensions import db
from models import Point, Review, Comment

points_bp = Blueprint('points', __name__)

DATABASE = (
    "prod-points.sqlite" if os.path.exists("prod-points.sqlite") else "points.sqlite"
)

@points_bp.route('/')
def index():
  points = Point.query.all()
  return jsonify(points)

@points_bp.route('/', methods=['POST'])
def create():
  # Create a point
  return Response("POST /api/v1/points", status=404, mimetype='application/json')

@points_bp.route('/<int:point_id>')
def show(point_id):
  point = Point.query.get(point_id)

  # Fix: Proper Error Handling and consistent messages
  if point is None:
    return Response(status=404)
  
  return jsonify(point)

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
