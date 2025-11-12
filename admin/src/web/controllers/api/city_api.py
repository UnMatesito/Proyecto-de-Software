from flask import jsonify
from core.services import city_service
from . import api_bp

@api_bp.get("/cities")
def list_cities():
    """
    GET /cities
    Devuelve todas las ciudades disponibles en la base de datos.
    """
    try:
        cities = city_service.get_all_cities()
        data = [
            {
                "id": city.id,
                "name": city.name,
                "province_id": city.province_id
            }
            for city in cities
        ]
        return jsonify({"data": data}), 200
    except Exception:
        return jsonify({
            "error": {
                "code": "server_error",
                "message": "An unexpected error occurred"
            }
        }), 500
