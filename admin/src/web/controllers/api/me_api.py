from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

from core.services import review_service, user_service
from web.schemas.reviews_schemas import MyReviewQuerySchema, MyReviewResponseSchema
from web.utils.format_marshmallow_validation_errors import format_validation_errors

from . import api_bp


@api_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = user_service.get_user_by_id(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    return (
        jsonify(
            {
                "id": user.id,
                "name": user.get_full_name(),
                "email": user.email,
                "avatar": user.avatar or None,
            }
        ),
        200,
    )


@api_bp.get("/me/reviews")
@jwt_required()
def list_my_reviews():
    """
    GET /api/me/reviews
    Devuelve las reseñas del usuario autenticado, incluyendo datos
    del sitio anidado para la vista de "Mi Perfil".
    """
    user_id = get_jwt_identity()

    schema = MyReviewQuerySchema()

    try:
        params = schema.load(request.args)
    except ValidationError as err:
        return (
            jsonify(
                {
                    "error": {
                        "code": "invalid_query",
                        "message": "Parameter validation failed",
                        "details": format_validation_errors(err.messages),
                    }
                }
            ),
            400,
        )

    try:
        pagination = review_service.get_user_reviews(
            user_id=user_id,
            page=params["page"],
            per_page=params["per_page"],
            sort=params["sort"],
        )

        data = MyReviewResponseSchema(many=True).dump(pagination.items)

        meta = {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "total_pages": pagination.pages,
        }

        return jsonify({"data": data, "meta": meta}), 200

    except Exception as e:
        print(f"Error en list_my_reviews: {e}")
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
def my_favorites():
    user_id = get_jwt_identity()

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    order_by = request.args.get("order_by", "id")
    sorted_by = request.args.get("sorted_by", "asc")

    try:
        # Usar el servicio existente
        paginated_result = user_service.get_user_favorites(
            user_id=user_id,
            page=page,
            per_page=per_page,
            order_by=order_by,
            sorted_by=sorted_by,
        )
    except ValueError as e:
        return jsonify({"error": {"code": "not_found", "message": str(e)}}), 404

    data = [
        {
            "id": site.id,
            "name": site.name,
            "short_description": site.brief_description,
            "description": site.full_description,
            "city": site.city.name if site.city else None,
            "province": (
                site.city.province.name if site.city and site.city.province else None
            ),
            "country": "AR",
            "lat": site.latitude,
            "lon": site.longitude,
            "tags": [tag.name for tag in site.tags],
            "state_of_conservation": (
                site.conservation_state.name if site.conservation_state else None
            ),
            "inserted_at": site.created_at.isoformat() if site.created_at else None,
            "updated_at": site.updated_at.isoformat() if site.updated_at else None,
        }
        for site in paginated_result.items
    ]

    return (
        jsonify(
            {
                "data": data,
                "meta": {
                    "page": paginated_result.page,
                    "per_page": paginated_result.per_page,
                    "total": paginated_result.total,
                    "pages": paginated_result.pages,
                },
            }
        ),
        200,
    )
