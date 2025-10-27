from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.models.review import Review  # suponiendo que existe
from core.models.historic_site import HistoricSite
from core.database import db
from . import api_bp

@api_bp.get("/sites/<int:site_id>/reviews")
@jwt_required()
def list_reviews(site_id):
    """Lista reseñas de un sitio"""
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 25))

    pagination = Review.query.filter_by(historic_site_id=site_id).paginate(page, per_page, False)
    reviews = [
        {
            "id": r.id,
            "user_id": r.user_id,
            "rating": r.rating,
            "content": r.content,
            "status": r.status,
            "created_at": r.created_at.isoformat(),
        }
        for r in pagination.items
    ]

    return jsonify({
        "items": reviews,
        "page": pagination.page,
        "pages": pagination.pages,
        "total": pagination.total,
    }), 200


@api_bp.post("/sites/<int:site_id>/reviews")
@jwt_required()
def create_review(site_id):
    """Crea una nueva reseña"""
    data = request.get_json() or {}
    user_id = get_jwt_identity()

    if not data.get("content") or not data.get("rating"):
        return jsonify({"error": "Faltan campos requeridos"}), 400

    existing = Review.query.filter_by(user_id=user_id, historic_site_id=site_id).first()
    if existing:
        return jsonify({"error": "Ya existe una reseña para este sitio"}), 400

    review = Review(
        user_id=user_id,
        historic_site_id=site_id,
        rating=data["rating"],
        content=data["content"],
        status="Pendiente",
    )

    db.session.add(review)
    db.session.commit()
    return jsonify({"id": review.id, "message": "Reseña creada"}), 201
