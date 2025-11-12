from flask import Blueprint

api_bp = Blueprint("api", __name__)

from . import auth_api, sites_api, favorites_api, reviews_api, feature_flag_api, province_api, city_api, tags_api, me_api
