from flask import Blueprint, flash, redirect, render_template, request, url_for

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
    """Lista las reseñas con filtros y paginación"""
    try:
        # Parámetros de paginación y orden
        order_by = request.args.get("order_by", "created_at")
        sorted_by = request.args.get(
            "sorted_by", "desc"
        )  # Más recientes primero por defecto
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

        # Validar que min no sea mayor que max
        if rating_min and rating_max and rating_min > rating_max:
            rating_min, rating_max = rating_max, rating_min

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
            {"key": "rating", "label": "Calificación", "render": "rating"},
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
            # Mantener los filtros en el template para repoblar el formulario
            current_filters={
                "status": status,
                "site_id": site_id,
                "rating_min": rating_min,
                "rating_max": rating_max,
                "date_from": date_from,
                "date_to": date_to,
                "search_email": search_email,
            },
        )
    except Exception as e:
        flash(f"Error al cargar reseñas: {str(e)}", "error")
        return redirect(url_for("main_bp.home"))


@review_bp.get("/<int:review_id>")
@login_required
@permission_required("review_show")
def detail(review_id):
    """Muestra los detalles de una reseña"""
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
    """
    Aprueba una reseña.
    El event listener actualiza automáticamente el rating del sitio histórico.
    """
    try:
        review = approve_review(review_id)

        flash(
            f"Reseña aprobada exitosamente. "
            f"Rating de '{review.historic_site.name}': "
            f"{review.historic_site.average_rating:.1f} "
            f"({review.historic_site.rating_count} reseñas)",
            "success",
        )

    except ValueError as e:
        # Error de validación (reseña no existe, ya aprobada, etc.)
        flash(str(e), "warning")
    except RuntimeError as e:
        # Error en la base de datos
        flash(f"Error al aprobar la reseña: {str(e)}", "error")
    except Exception as e:
        # Error inesperado
        flash(f"Error inesperado: {str(e)}", "error")

    return redirect(url_for("reviews.index"))


@review_bp.post("/<int:review_id>/reject")
@login_required
@permission_required("review_reject")
def reject(review_id):
    """
    Rechaza una reseña con motivo.
    Si estaba aprobada, el event listener actualiza el rating del sitio.
    """
    reason = request.form.get("reason", "").strip()

    if not reason:
        flash("Debe ingresar un motivo para el rechazo.", "error")
        return redirect(url_for("reviews.detail", review_id=review_id))

    if len(reason) < 5:
        flash("El motivo de rechazo debe tener al menos 5 caracteres.", "error")
        return redirect(url_for("reviews.detail", review_id=review_id))

    try:
        reject_review_serv(review_id=review_id, reason=reason)

        flash(f"Reseña rechazada correctamente. Motivo: {reason[:50]}...", "success")

    except ValueError as e:
        flash(str(e), "warning")
    except RuntimeError as e:
        flash(f"Error al rechazar la reseña: {str(e)}", "error")
    except Exception as e:
        flash(f"Error inesperado: {str(e)}", "error")

    return redirect(url_for("reviews.index"))


@review_bp.post("/<int:review_id>/delete")
@login_required
@permission_required("review_destroy")
def delete(review_id):
    """
    Elimina definitivamente una reseña.
    Si estaba aprobada, el event listener actualiza el rating del sitio.
    """
    try:
        # Obtener info antes de eliminar (para el mensaje)
        review = get_review_by_id(review_id)
        if not review:
            flash("Reseña no encontrada", "warning")
            return redirect(url_for("reviews.index"))

        site_name = review.historic_site.name
        was_approved = review.is_approved()

        # Eliminar
        delete_review(review_id)

        # Mensaje informativo
        if was_approved:
            flash(
                f"Reseña eliminada. El rating de '{site_name}' ha sido actualizado.",
                "success",
            )
        else:
            flash("Reseña eliminada correctamente.", "success")

    except ValueError as e:
        flash(str(e), "warning")
    except RuntimeError as e:
        flash(f"Error al eliminar la reseña: {str(e)}", "error")
    except Exception as e:
        flash(f"Error inesperado: {str(e)}", "error")

    return redirect(url_for("reviews.index"))
