from flask import jsonify

from core.services import city_service, province_service

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

@api_bp.get("/provinces/<int:province_id>/cities")
def list_cities_by_province(province_id):
    """
    GET /provinces/{province_id}/cities
    Devuelve todas las ciudades que pertenecen a una provincia en particular.
    """
    try:
        # Verificar que la provincia exista
        province = province_service.get_province_by_id(province_id)
        if not province:
            return jsonify({
                "error": {
                    "code": "not_found",
                    "message": "Province not found"
                }
            }), 404

        # Obtener ciudades de la provincia
        cities = city_service.get_city_by_province(province_id)
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