from flask import Blueprint

api_bp = Blueprint("api", __name__)

from . import auth_api, sites_api, favorites_api, reviews_api
