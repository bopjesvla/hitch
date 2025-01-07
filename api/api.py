from flask import Blueprint
from api.v1.points import points_bp

api_bp = Blueprint('api', __name__)

api_bp.register_blueprint(points_bp, url_prefix='/points')
