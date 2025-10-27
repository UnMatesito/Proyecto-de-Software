from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from core.services.historic_site_service import get_all_historic_site
from core.services.review_service import (
    approve_review,
    delete_review,
    get_paginated_reviews,
    get_review_by_id,
)
from core.services.review_service import reject_review as reject_review_serv
from web.utils.auth import login_required, permission_required

review_bp = Blueprint("reviews", __name__, url_prefix="/reviews")


@review_bp.get("/")
@login_required
@permission_required("review_index")
def index():
    """Lista las reseñas y opciones"""
    try:
        # Parámetros de paginación y orden
        order_by = request.args.get("order_by", "created_at")
        sorted_by = request.args.get("sorted_by", "asc")
        page = request.args.get("page", 1, type=int)

        # Filtro de estado
        status_param = None
        status = request.args.get("status", None)
        if status == "pending":
            status_param = "Pendiente"
        elif status == "approved":
            status_param = "Aprobada"
        elif status == "rejected":
            status_param = "Rechazada"

        # Filtro de historic_site
        site_id = request.args.get("site_id", None)
        if site_id:
            try:
                site_id = int(site_id)
            except ValueError:
                site_id = None

        # Filtro de calificación
        rating_min = request.args.get("rating_min", type=int)
        rating_max = request.args.get("rating_max", type=int)

        # Filtro de fecha
        date_from = request.args.get("date_from")
        date_to = request.args.get("date_to")

        # Filtro de búsqueda por correo
        search_email = request.args.get("search_email")

        # Construir diccionario de filtros
        filters = {}
        if status_param:
            filters["status"] = status_param
        if site_id is not None:
            filters["historic_site_id"] = site_id
        if rating_min:
            filters["rating_min"] = rating_min
        if rating_max:
            filters["rating_max"] = rating_max
        if date_from:
            filters["date_from"] = date_from
        if date_to:
            filters["date_to"] = date_to
        if search_email:
            filters["search_text"] = search_email

        # Obtener sitios para el select
        sites = get_all_historic_site()

        # Columnas de la tabla
        columns = [
            {"key": "id", "label": "ID"},
            {"key": "site_name", "label": "Sitio", "render": "site_name"},
            {"key": "rating", "label": "Calificacion", "render": "rating"},
            {"key": "status", "label": "Estado", "render": "status"},
            {"key": "user_name", "label": "Usuario", "render": "review_user_name"},
            {"key": "created_at", "label": "Creado", "render": "date"},
            {"key": "content", "label": "Contenido", "render": "content"},
        ]

        # Obtener reseñas paginadas
        reviews_page = get_paginated_reviews(
            page=page, order_by=order_by, order_dir=sorted_by, filters=filters
        )

        return render_template(
            "reviews/index.html",
            pagination=reviews_page,
            columns=columns,
            sites=sites,
            order_by=order_by,
            sorted_by=sorted_by,
        )
    except Exception as e:
        flash(f"Error al cargar reseñas: {str(e)}", "error")
        return redirect(url_for("main_bp.home"))


@review_bp.get("/<int:review_id>")
@login_required
@permission_required("review_show")
def detail(review_id):
    """Informacion de una reseña"""
    try:
        review = get_review_by_id(review_id)
        if not review:
            flash("Reseña no encontrada", "error")
            return redirect(url_for("reviews.index"))
        return render_template("reviews/detail.html", review=review)
    except Exception as e:
        flash(f"Error al cargar la reseña: {str(e)}", "error")
        return redirect(url_for("reviews.index"))


@review_bp.post("/<int:review_id>/approve")
@login_required
@permission_required("review_approve")
def approve(review_id):
    """Aprueba una reseña"""
    try:
        approve_review(review_id)
        flash("Reseña aprobada", "success")
    except ValueError as e:
        flash(str(e), "warning")
    except RuntimeError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Error inesperado: {str(e)}", "error")
    return redirect(url_for("reviews.index"))


@review_bp.post("/<int:review_id>/delete")
@login_required
@permission_required("review_destroy")
def delete(review_id):
    """Elimina una reseña"""
    try:
        delete_review(review_id)
        flash("Reseña eliminada", "success")
    except ValueError as e:
        flash(str(e), "warning")
    except RuntimeError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Error inesperado: {str(e)}", "error")
    return redirect(url_for("reviews.index"))


@review_bp.post("/<int:review_id>/reject")
@login_required
@permission_required("review_reject")
def reject(review_id):
    """Rechaza una review"""
    reason = request.form.get("reason", "").strip()
    if not reason:
        flash("Debe ingresar un motivo para el rechazo.", "error")
        return redirect(url_for("reviews.index"))
    try:
        reject_review_serv(review_id=review_id, reason=reason)
        flash("La reseña fue rechazada correctamente.", "success")
    except ValueError as e:
        flash(str(e), "warning")
    except RuntimeError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Error inesperado: {str(e)}", "error")
    return redirect(url_for("reviews.index"))
