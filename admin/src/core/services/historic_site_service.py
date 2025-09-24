from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError

from core.database import db
from core.models import HistoricSite
from core.services import category_service, city_service, conservation_state_service


def get_all_historic_site():
    """Obtiene todos los sitios históricos."""
    return HistoricSite.query.all()


def get_published_historic_sites():
    """Obtiene todos los sitios históricos publicados (visibles, validados y no eliminados)."""
    return HistoricSite.query.filter(
        HistoricSite.is_visible == True,
        HistoricSite.pending_validation == False,
        HistoricSite.deleted_at.is_(None),
    ).all()


def get_pending_historic_sites():
    """Obtiene todos los sitios históricos pendientes de validación y no eliminados."""
    return HistoricSite.query.filter(
        HistoricSite.pending_validation == True, HistoricSite.deleted_at.is_(None)
    ).all()


def create_historic_site(**kwargs):
    """Crea un nuevo sitio histórico."""
    historic_site = HistoricSite(**kwargs)
    db.session.add(historic_site)
    db.session.commit()
    return historic_site


def get_historic_site_by_id(site_id: int):
    """Obtiene un sitio histórico por su ID."""
    site = HistoricSite.query.get(site_id)
    if not site:
        raise ValueError(f"No existe el sitio histórico con id {site_id}")
    return site


def assign_relations_to_historic_site(
    historic_site, conservation_state, categories, user, city, tags=None
):
    """Asigna relaciones a un sitio histórico."""
    historic_site.conservation_state = conservation_state
    historic_site.categories = categories
    historic_site.user = user
    historic_site.city = city
    if tags:
        for t in tags:
            historic_site.add_tag(t)
    db.session.commit()
    return historic_site


def update_conservation_state(site_id, conservation_id):
    """Actualiza el estado de conservación de un sitio histórico."""
    site = get_historic_site_by_id(site_id)
    conservation_state = conservation_state_service.get_conservation_state_by_id(
        conservation_id
    )
    site.conservation_state = conservation_state
    site.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return site


def update_category_site(site_id, category_id):
    """Actualiza la categoría de un sitio histórico."""
    site = get_historic_site_by_id(site_id)
    category = category_service.get_category_by_id(category_id)
    if category not in site.categories:
        site.categories.append(category)
    site.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return site


def update_city(site_id, city_id):
    """Actualiza la ciudad de un sitio histórico."""
    site = get_historic_site_by_id(site_id)
    city = city_service.get_city_by_id(city_id)
    site.city = city
    site.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return site


def assign_tags(site_id, tag_ids):
    """Asigna una lista de tags a un sitio histórico, reemplazando los existentes."""
    if not tag_ids:
        raise ValueError("Se requiere al menos un tag")

    site = get_historic_site_by_id(site_id)

    from core.services import tag_service

    tags = []
    for tag_id in tag_ids:
        tag = tag_service.get_tag_by_id(tag_id)
        tags.append(tag)

    # Limpiar tags existentes y asignar nuevos usando métodos del modelo
    for tag in list(site.tags):
        site.remove_tag(tag)
    for tag in tags:
        site.add_tag(tag)

    site.updated_at = datetime.now(timezone.utc)

    try:
        db.session.commit()
        return site
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error al asignar tags: {e}")


def add_tags(site_id, tag_ids):
    """Agrega tags adicionales a un sitio histórico sin eliminar los existentes."""
    if not tag_ids:
        raise ValueError("Se requiere al menos un tag")

    site = get_historic_site_by_id(site_id)
    current_tag_ids = [tag.id for tag in site.tags]

    from core.services import tag_service

    for tag_id in tag_ids:
        if tag_id not in current_tag_ids:
            tag = tag_service.get_tag_by_id(tag_id)
            site.add_tag(tag)

    site.updated_at = datetime.now(timezone.utc)

    try:
        db.session.commit()
        return site
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error al agregar tags: {e}")


def delete_historic_site(site_id):
    """Marca un sitio histórico como eliminado usando el método del modelo."""
    site = get_historic_site_by_id(site_id)
    if site.is_deleted():
        raise ValueError(f"El sitio histórico {site.name} ya está eliminado")
    site.delete_site()
    try:
        db.session.commit()
        return site
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error al eliminar el sitio histórico: {e}")
