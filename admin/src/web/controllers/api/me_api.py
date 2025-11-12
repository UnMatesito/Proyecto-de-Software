from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.orm import joinedload

#from core.models.favorite import Favorite
from core.database import db
from core.models import Review
from core.models.user import User
from core.services import user_service
from web.schemas.reviews_schemas import MyReviewResponseSchema, ReviewQuerySchema
from web.utils.format_marshmallow_validation_errors import format_validation_errors

from . import api_bp


@api_bp.route("/user/me", methods=["GET"])
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

    try:
        page = int(request.args.get("page", 1))
        per_page = 25 
        if page < 1:
            page = 1

        sort = request.args.get("sort", "date_desc")

        query = Review.query.filter_by(user_id=user_id)
        
        query = query.options(joinedload(Review.historic_site))
        

        if sort == "date_asc":
            query = query.order_by(Review.created_at.asc())
        else:
            query = query.order_by(Review.created_at.desc())

        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        data = MyReviewResponseSchema(many=True).dump(pagination.items)
        
        meta = {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }

        return jsonify({"data": data, "meta": meta}), 200

    except Exception as e:
        print(f"Error en list_my_reviews: {e}") 
        return jsonify({
            "error": {"code": "server_error", "message": "An unexpected error occurred"}
        }), 500