from flask import jsonify

from core.services import tag_service

from . import api_bp


@api_bp.get("/tags")
def list_tags():
    """
    GET /tags
    Devuelve todas las etiquetas disponibles.
    """
    try:
        tags = tag_service.get_all_not_deleted_tags()
        data = [
            {
                "id": tag.id,
                "name": tag.name,
                "slug": tag.slug,
            }
            for tag in tags
        ]
        return jsonify({"data": data}), 200
    except Exception:
        return jsonify({
            "error": {
                "code": "server_error",
                "message": "An unexpected error occurred"
            }
        }), 500
