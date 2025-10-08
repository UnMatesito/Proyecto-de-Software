from flask import Blueprint, jsonify, flash
from core.services import get_province_by_id
from web.utils.auth import login_required, permission_required

city_bp = Blueprint("city_bp", __name__, url_prefix="/cities")

@login_required
@permission_required("city_index")
@city_bp.get("/<int:province_id>")
def get_cities(province_id):
    """Retorna las ciudades de una provincia, determinada por su ID que se envía como parámetro en la URL."""
    try:
        province = get_province_by_id(province_id)
        return jsonify([{"id": c.id, "name": c.name} for c in province.cities])
    except Exception as e:
        flash(f"Error al buscar la ciudades, error: {e}", "error")
        return jsonify([{"id": "", "name": ""}])
