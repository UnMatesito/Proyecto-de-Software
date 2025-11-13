from flask import Blueprint

api_bp = Blueprint("api", __name__)

from . import (
    auth_api,
    city_api,
    favorites_api,
    feature_flag_api,
    me_api,
    province_api,
    reviews_api,
    sites_api,
    tags_api,
)
