from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.models.favorite import Favorite  # suponiendo modelo intermedio
from core.database import db
from . import api_bp

@api_bp.put("/sites/<int:site_id>/favorite")
@jwt_required()
def add_favorite(site_id):
    user_id = get_jwt_identity()
    fav = Favorite.query.filter_by(user_id=user_id, historic_site_id=site_id).first()
    if not fav:
        fav = Favorite(user_id=user_id, historic_site_id=site_id)
        db.session.add(fav)
        db.session.commit()
    return "", 204


@api_bp.delete("/sites/<int:site_id>/favorite")
@jwt_required()
def remove_favorite(site_id):
    user_id = get_jwt_identity()
    fav = Favorite.query.filter_by(user_id=user_id, historic_site_id=site_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
    return "", 204
