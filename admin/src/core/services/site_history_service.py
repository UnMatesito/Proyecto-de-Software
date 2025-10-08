from datetime import datetime

from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError

from core.database import db
from core.utils import pagination, search

from ..models import SiteHistory


def create_site_history(historic_site_id, user_id, event_type, description):
    """Crea un registro en SiteHistory."""
    try:
        site_history = SiteHistory(
            historic_site_id=historic_site_id,
            user_id=user_id,
            event_type_id=event_type.id,
            description=description,
        )
        db.session.add(site_history)
        return site_history

    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error al crear historial del sitio: {str(e)}") from e


def get_paginated_site_histories(site_id, page=1, per_page=25, filters=None):
    """Obtiene los historiales de sitios con paginación.

    Args:
        site_id (int): ID del sitio
        page (int): número de página
        per_page (int): elementos por página
        filters (dict): filtros a aplicar
    Returns:
        dict con paginación
    """
    filters = filters or {}
    filters["historic_site_id"] = site_id
    # Construir query con el GenericSearchBuilder
    query = search.build_search_query(SiteHistory, filters)

    query = search.apply_ordering(
        query, SiteHistory, order_by="created_at", order_dir="desc"
    )

    return pagination.paginate_query(query, page=page, per_page=per_page)
