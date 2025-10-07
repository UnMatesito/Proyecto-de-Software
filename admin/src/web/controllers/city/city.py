from flask import (
    Blueprint,
    jsonify,
)

from core.services import get_province_by_id

city_bp = Blueprint("city_bp", __name__, url_prefix="/cities")


@city_bp.get("/<int:province_id>")
def get_cities(province_id):
    try: 
        province = get_province_by_id(province_id)
        return jsonify([{"id": c.id, "name": c.name} for c in province.cities])
    except Exception as e :
         return jsonify([{"id": "", "name": ""}])
