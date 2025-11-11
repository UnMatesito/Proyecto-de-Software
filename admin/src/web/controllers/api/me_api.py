from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
#from core.models.favorite import Favorite
from core.database import db
from . import api_bp
from core.services import user_service
from core.models.user import User

@api_bp.get("/me/favorites")
@jwt_required()
def my_favorites():
    user_id = get_jwt_identity()
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 25))

    pagination = Favorite.query.filter_by(user_id=user_id).paginate(page, per_page, False)
    data = [
        {
            "site_id": f.historic_site.id,
            "name": f.historic_site.name,
            "city": f.historic_site.city.name if f.historic_site.city else None,
        }
        for f in pagination.items
    ]

    return jsonify({
        "items": data,
        "page": pagination.page,
        "pages": pagination.pages,
        "total": pagination.total,
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
