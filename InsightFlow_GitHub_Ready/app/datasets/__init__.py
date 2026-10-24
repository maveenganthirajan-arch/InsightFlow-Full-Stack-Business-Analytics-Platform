from flask import Blueprint

datasets_bp = Blueprint('datasets', __name__)

from . import routes
