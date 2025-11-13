from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

from core.services import user_service
from web.schemas import FavoriteQuerySchema

from . import api_bp


@api_bp.put("/sites/<int:site_id>/favorite")
@jwt_required()
def add_favorite(site_id):
    """
    PUT /sites/{site_id}/favorite
    Agrega un sitio a los favoritos del usuario autenticado.
    """
    user_id = get_jwt_identity()
    try:
        user_service.add_favorite_site(user_id, site_id)
        return "", 204
    except ValueError as err:
        return jsonify({"error": {"code": "not_found", "message": err.args[0]}}), 404
    except Exception:
        return (
            jsonify(
                {
                    "error": {
                        "code": "server_error",
                        "message": "An unexpected error occurred",
                    }
                }
            ),
            500,
        )


@api_bp.delete("/sites/<int:site_id>/favorite")
@jwt_required()
def remove_favorite(site_id):
    """
    DELETE /sites/{site_id}/favorite
    Elimina un sitio del usuario autenticado.
    """
    user_id = get_jwt_identity()
    try:
        user_service.remove_favorite_site(user_id, site_id)
        return "", 204
    except ValueError:
        return (
            jsonify({"error": {"code": "not_found", "message": "Site not found"}}),
            404,
        )
    except Exception:
        return (
            jsonify(
                {
                    "error": {
                        "code": "server_error",
                        "message": "An unexpected error occurred",
                    }
                }
            ),
            500,
        )


@api_bp.get("/me/favorites")
@jwt_required()
def list_favorites():
    """
    GET /me/favorites
    Obtiene la lista de sitios favoritos del usuario autenticado.
    """
    user_id = get_jwt_identity()

    # Validar parámetros con schema
    schema = FavoriteQuerySchema()
    try:
        params = schema.load(request.args)
    except ValidationError as err:
        return (
            jsonify(
                {
                    "error": {
                        "code": "invalid_query",
                        "message": "Parameter validation failed",
                        "details": err.messages,
                    }
                }
            ),
            400,
        )

    try:
        # Usar parámetros validados
        pagination = user_service.get_user_favorites(
            user_id,
            params["page"],
            params["per_page"],
            params["order_by"],
            params["sorted_by"],
        )

        data = [
            {
                "id": site.id,
                "name": site.name,
                "short_description": site.brief_description,
                "description": site.full_description,
                "review_count": site.rating_count,
                "average_rating": site.average_rating,
                "city": site.city.name if site.city else None,
                "province": (
                    site.city.province.name
                    if site.city and site.city.province
                    else None
                ),
                "lat": site.latitude,
                "lon": site.longitude,
                "tags": [t.slug for t in site.tags],
                "state_of_conservation": (
                    site.conservation_state.state if site.conservation_state else None
                ),
                "inauguration_year": site.inauguration_year,
                "category": site.category.name if site.category else None,
                "inserted_at": (
                    site.created_at.isoformat() + "Z" if site.created_at else None
                ),
                "updated_at": (
                    site.updated_at.isoformat() + "Z" if site.updated_at else None
                ),
            }
            for site in pagination["items"]
        ]

        meta = {
            "page": pagination["current_page"],
            "per_page": pagination["per_page"],
            "total": pagination["total"],
            "total_pages": pagination["pages"],
        }

        return jsonify({"data": data, "meta": meta}), 200

    except ValueError:
        return (
            jsonify({"error": {"code": "not_found", "message": "Site not found"}}),
            404,
        )

    except Exception:
        return (
            jsonify(
                {
                    "error": {
                        "code": "server_error",
                        "message": "An unexpected error occurred",
                    }
                }
            ),
            500,
        )
