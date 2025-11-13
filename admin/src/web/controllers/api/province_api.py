from flask import jsonify

from core.services import province_service

from . import api_bp


@api_bp.get("/provinces")
def list_provinces():
    """
    GET /provinces
    Devuelve todas las provincias disponibles en la base de datos.
    """
    try:
        provinces = province_service.get_all_provinces()
        data = [
            {
                "id": province.id,
                "name": province.name
            }
            for province in provinces
        ]
        return jsonify({"data": data}), 200
    except Exception:
        return jsonify({
            "error": {
                "code": "server_error",
                "message": "An unexpected error occurred"
            }
        }), 500
