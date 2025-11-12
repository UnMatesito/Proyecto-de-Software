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
    try:
        full_name = user.get_full_name()
    except Exception as e:
        return jsonify({"msg": "Error interno al procesar nombre"}), 500

    try:
        avatar_url = user.avatar or None
    except Exception as e:
        return jsonify({"msg": "Error interno al procesar avatar"}), 500

    return jsonify({
        "id": user.id,
        "name": user.get_full_name(),
        "email": user.email,
        "avatar": user.avatar or None,
    }), 200


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