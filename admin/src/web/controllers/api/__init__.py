from flask import Blueprint

from ...utils.hooks import hook_portal_maintenance

api_bp = Blueprint("api", __name__)


@api_bp.before_request
def enforce_portal_maintenance():
    """Evita el acceso a la API cuando el portal está en mantenimiento."""
    return hook_portal_maintenance()

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