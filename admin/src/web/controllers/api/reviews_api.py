from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from core.database import db
from core.models import Review
from core.services import review_service, historic_site_service
from core.utils.search import search_with_pagination
from . import api_bp


@api_bp.get("/sites/<int:site_id>/reviews")
@jwt_required()
def list_reviews(site_id):
    """
    GET /sites/{site_id}/reviews
    Devuelve una lista paginada de reseñas para un sitio histórico específico.
    Usa los métodos genéricos de búsqueda y paginación.
    """
    try:
        # Validar que el sitio exista
        historic_site_service.get_published_site_by_id(site_id)
    except ValueError:
        return jsonify({
            "error": {"code": "not_found", "message": "Site not found"}
        }), 404

    # Obtener parámetros de paginación
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        order_by = request.args.get("order_by", "created_at")
        order_dir = request.args.get("sorted_by", "desc")
    except ValueError:
        return jsonify({
            "error": {
                "code": "invalid_query",
                "message": "Invalid pagination parameters"
            }
        }), 400

    filters = {"historic_site_id": site_id}

    try:
        # Usa search_with_pagination del core
        pagination = search_with_pagination(
            Review,
            filters=filters,
            page=page,
            per_page=per_page,
            order_by=order_by,
            order_dir=order_dir,
            text_search_columns=["content"]
        )

        data = [
            {
                "id": r.id,
                "site_id": r.historic_site_id,
                "rating": r.rating,
                "comment": r.content,
                "inserted_at": r.created_at.isoformat() + "Z",
                "updated_at": r.updated_at.isoformat() + "Z"
            }
            for r in pagination["items"]
        ]

        meta = {
            "page": pagination["current_page"],
            "per_page": pagination["per_page"],
            "total": pagination["total"],
        }

        return jsonify({"data": data, "meta": meta}), 200

    except Exception:
        return jsonify({
            "error": {"code": "server_error", "message": "An unexpected error occurred"}
        }), 500


@api_bp.post("/sites/<int:site_id>/reviews")
@jwt_required()
def create_review(site_id):
    """
    POST /sites/{site_id}/reviews
    Crea una nueva reseña para un sitio histórico específico.
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    # Validar campos requeridos
    rating = data.get("rating")
    comment = data.get("comment")

    if rating is None or comment is None:
        return jsonify({
            "error": {
                "code": "invalid_data",
                "message": "Invalid input data",
                "details": {
                    "rating": ["This field is required"],
                    "comment": ["This field is required"]
                }
            }
        }), 400

    try:
        review = review_service.create_review(
            user_id=user_id,
            site_id=site_id,
            rating=int(rating),
            content=comment.strip(),
        )
        return jsonify({
            "id": review.id,
            "site_id": site_id,
            "rating": review.rating,
            "comment": review.content,
            "inserted_at": review.created_at.isoformat() + "Z",
            "updated_at": review.updated_at.isoformat() + "Z"
        }), 201

    except ValueError as e:
        msg = str(e).lower()
        if "ya dejó" in msg:
            details = {"site_id": ["User already reviewed this site"]}
        elif "rango" in msg or "calificación" in msg:
            details = {"rating": ["Must be between 1 and 5"]}
        elif "sitio" in msg:
            return jsonify({
                "error": {"code": "not_found", "message": "Site not found"}
            }), 404
        else:
            details = {"comment": [str(e)]}

        return jsonify({
            "error": {
                "code": "invalid_data",
                "message": "Invalid input data",
                "details": details
            }
        }), 400

    except Exception:
        db.session.rollback()
        return jsonify({
            "error": {"code": "server_error", "message": "An unexpected error occurred"}
        }), 500


@api_bp.get("/sites/<int:site_id>/reviews/<int:review_id>")
@jwt_required()
def get_review(site_id, review_id):
    """
    GET /sites/{site_id}/reviews/{review_id}
    Devuelve una reseña específica.
    """
    try:
        review = Review.query.filter_by(
            id=review_id,
            historic_site_id=site_id
        ).first()

        if not review:
            return jsonify({
                "error": {"code": "not_found", "message": "Review not found"}
            }), 404

        return jsonify({
            "id": review.id,
            "site_id": review.historic_site_id,
            "rating": review.rating,
            "comment": review.content,
            "inserted_at": review.created_at.isoformat() + "Z",
            "updated_at": review.updated_at.isoformat() + "Z"
        }), 200

    except Exception:
        return jsonify({
            "error": {"code": "server_error", "message": "An unexpected error occurred"}
        }), 500


@api_bp.delete("/sites/<int:site_id>/reviews/<int:review_id>")
@jwt_required()
def delete_review(site_id, review_id):
    """
    DELETE /sites/{site_id}/reviews/{review_id}
    Elimina una reseña del usuario autenticado.
    """
    user_id = get_jwt_identity()
    try:
        review = Review.query.get(review_id)
        if not review or review.historic_site_id != site_id:
            return jsonify({
                "error": {"code": "not_found", "message": "Review not found"}
            }), 404
        if review.user_id != user_id:
            return jsonify({
                "error": {
                    "code": "forbidden",
                    "message": "You do not have permission to delete this review"
                }
            }), 403

        review_service.delete_review(review_id)
        return "", 204

    except Exception:
        db.session.rollback()
        return jsonify({
            "error": {"code": "server_error", "message": "An unexpected error occurred"}
        }), 500
