from flask import Blueprint, flash, redirect, render_template, request, url_for

from core.services.event_type_service import get_all_event_types
from core.services.historic_site_service import get_historic_site_by_id
from core.services.site_history_service import get_paginated_site_histories
from core.services.user_service import get_user_history
from web.utils.auth import login_required, permission_required

site_history_bp = Blueprint("site_history", __name__, url_prefix="/site")


@site_history_bp.get("/<int:site_id>/history")
@login_required
@permission_required("site_history")
def view_site_history(site_id):
    """Vista para mostrar el historial de un sitio específico con paginación y filtros."""
    try:
        site = get_historic_site_by_id(site_id)
        if not site:
            flash("El sitio no existe.", "error")
            return redirect(url_for("site_bp.list_paginated_sites"))
        page = request.args.get("page", 1, type=int)
        filters = {
            "user_id": request.args.get("user_id", type=int),
            "event_type_id": request.args.get("event_type", type=int),
            "date_from": request.args.get("date_from", type=str),
            "date_to": request.args.get("date_to", type=str),
        }

        pagination = get_paginated_site_histories(
            site_id=site_id, filters=filters, page=page, per_page=25
        )

        site_history = pagination["items"]
        event_types = get_all_event_types()
        users = get_user_history()

        columns = [
            {"key": "created_at",
             "label": "Fecha y Hora",
             "render": lambda h: h.created_at.strftime("%d/%m/%Y %H:%M"),
            },
            {
                "key": "event_type.name",
                "label": "Tipo de Acción",
                "render": lambda h: h.event_type.name,
            },
            {"key": "user.email", "label": "Usuario", "render": lambda h: h.user.email},
            {"key": "description", "label": "Descripción"},
        ]

        back_url = request.args.get("next")

        return render_template(
            "historic_site/site_history.html",
            site_history=site_history,
            site_name=site.name,
            site_id=site_id,
            pagination=pagination,
            columns=columns,
            event_types=event_types,
            users=users,
            back_url=back_url,
        )

    except Exception as e:
        flash(f"Error al cargar el historial: {e}", "error")
        return render_template(
            "historic_site/site_history.html",
            site_history=[],
            site_name="",
            site_id=site_id,
            pagination={
                "items": [],
                "pages": 0,
                "page_range": [],
                "has_prev": False,
                "has_next": False,
                "current_page": 1,
            },
            columns=[],
            event_types=[],
            users=[],
        )
