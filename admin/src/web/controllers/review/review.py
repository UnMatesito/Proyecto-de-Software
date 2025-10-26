from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from core.services.review_service import (
    approve_review,
    get_paginated_reviews,
    delete_review,
    reject_review as reject_review_serv

)





review_bp = Blueprint("reviews", __name__, url_prefix="/reviews")

@review_bp.get("/")
def index():
    page = request.args.get("page", 1)
    columns = [
        {"key": "id", "label": "ID"},
        {"key": "site_name", "label": "Sitio", "render": "site_name"},
        {"key": "rating", "label": "Calificacion"},
        {"key": "status", "label": "Estado", "render": "status"},
        {"key": "user_name", "label": "Usuario", "render": "review_user_name"},
        {"key": "created_at", "label": "Creado", "render": "date"},
    ]
    reviews_page= get_paginated_reviews(page=page)

    return render_template("reviews/index.html", pagination= reviews_page, columns=columns)


@review_bp.post("/<int:review_id>/approve")
def approve(review_id):
    approve_review(review_id)
    return None

@review_bp.post("/<int:review_id>/delete")
def delete(review_id):
    delete_review(review_id)
    return None

@review_bp.post("/<int:review_id>/reject")
def reject_review(review_id):
    reason = request.form.get("reason", "").strip()
    if not reason:
        flash("Debe ingresar un motivo para el rechazo.", "error")
        return redirect(url_for("reviews.index"))
    reject_review_serv(review_id=review_id, reason=reason)
    flash("La reseña fue rechazada correctamente.", "success")
    return redirect(url_for("reviews.index"))