from flask import Blueprint
from api.v1.points import points_bp

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

api_bp.register_blueprint(points_bp)
