from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.services.user_service import get_user_favorites
from core.database import db
from . import api_bp
from core.services import user_service
from core.models.user import User

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
        paginated_result = get_user_favorites(
            user_id=user_id,
            page=page,
            per_page=per_page,
            order_by=order_by,
            sorted_by=sorted_by
        )
    except ValueError as e:
        return jsonify({
            "error": {
                "code": "not_found",
                "message": str(e)
            }
        }), 404

    data = [
        {
            "id": site.id,
            "name": site.name,
            "short_description": site.brief_description,
            "description": site.full_description,
            "city": site.city.name if site.city else None,
            "province": site.city.province.name if site.city and site.city.province else None,
            "country": "AR",
            "lat": site.latitude,
            "long": site.longitude,
            "tags": [tag.name for tag in site.tags],
            "state_of_conservation": site.conservation_state.name if site.conservation_state else None,
            "inserted_at": site.created_at.isoformat() if site.created_at else None,
            "updated_at": site.updated_at.isoformat() if site.updated_at else None,
        }
        for site in paginated_result.items
    ]

    return jsonify({
        "data": data,
        "meta": {
            "page": paginated_result.page,
            "per_page": paginated_result.per_page,
            "total": paginated_result.total,
            "pages": paginated_result.pages
        }
    }), 200


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
