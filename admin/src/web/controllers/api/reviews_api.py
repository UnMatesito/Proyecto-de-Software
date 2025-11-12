from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from core.database import db
from core.models import Review
from core.services import (
    get_feature_flag_by_name,
    historic_site_service,
    review_service,
)
from core.utils.search import search_with_pagination
from web.schemas import (
    ReviewCreateSchema,
    ReviewQuerySchema,
    ReviewResponseSchema,
)
from web.utils.format_marshmallow_validation_errors import format_validation_errors
from . import api_bp



def _reviews_feature_blocked_response():
    flag = get_feature_flag_by_name("reviews_enabled")

    if flag and not flag.is_enabled:
        return (
            jsonify(
                {
                    "error": {
                        "code": "feature_disabled",
                        "message": flag.maintenance_message or "Reviews are disabled",
                    }
                }
            ),
            503,
        )

    return None


@api_bp.get("/sites/<int:site_id>/reviews")
@jwt_required()
def list_reviews(site_id):
    """
    GET /sites/{site_id}/reviews
    Devuelve una lista paginada de reseñas para un sitio histórico específico.
    Usa los métodos genéricos de búsqueda y paginación.
    """
    try:
        historic_site_service.get_published_site_by_id(site_id)
    except ValueError:
        return jsonify({
            "error": {"code": "not_found", "message": "Site not found"}
        }), 404

    # Validar parámetros de query
    schema = ReviewQuerySchema()
    try:
        params = schema.load(request.args)
    except ValidationError as err:
        return jsonify(format_validation_errors(err)), 400

    try:
        # Buscar reseñas con paginación y filtros
        pagination = search_with_pagination(
            Review,
            filters={"historic_site_id": site_id},
            page=params["page"],
            per_page=params["per_page"],
            order_by=params["order_by"],
            order_dir=params["sorted_by"],
            text_search_columns=["content"]
        )

        data = ReviewResponseSchema(many=True).dump(pagination["items"])
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
    Crea una nueva reseña para un sitio histórico.
    """
    user_id = get_jwt_identity()

    # Verificar si la funcionalidad de creación de reseñas está habilitada
    blocked_response = _reviews_feature_blocked_response()
    if blocked_response:
        return blocked_response

    schema = ReviewCreateSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify(format_validation_errors(err)), 400

    try:
        review = review_service.create_review(
            user_id=user_id,
            site_id=site_id,
            rating=data["rating"],
            content=data["comment"],
        )
        return jsonify(ReviewResponseSchema().dump(review)), 201

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
            id=review_id, historic_site_id=site_id
        ).first()

        if not review:
            return jsonify({
                "error": {"code": "not_found", "message": "Review not found"}
            }), 404

        return jsonify(ReviewResponseSchema().dump(review)), 200

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