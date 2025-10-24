from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.models.favorite import Favorite
from core.database import db
from . import api_bp

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
