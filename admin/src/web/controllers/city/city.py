from flask import (
    Blueprint,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from core.services import get_province_by_id

city_bp = Blueprint("city_bp", __name__, url_prefix="/cities")


@city_bp.get("/<int:province_id>")
def get_cities(province_id):
    province = get_province_by_id(province_id)
    return jsonify([{"id": c.id, "name": c.name} for c in province.cities])
