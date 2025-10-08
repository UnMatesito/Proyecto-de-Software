from datetime import datetime, timezone

from geoalchemy2.elements import WKTElement
from sqlalchemy.exc import SQLAlchemyError

from core.database import db
from core.models import HistoricSite
from core.services import (
    category_service,
    city_service,
    conservation_state_service,
    tag_service,
)
from core.utils.pagination import paginate_query
from core.utils.search import apply_ordering, build_search_query


def get_all_historic_site():
    """Obtiene todos los sitios históricos."""
    return HistoricSite.query.all()


def get_published_historic_sites():
    """Obtiene todos los sitios históricos publicados (visibles, validados y no eliminados)."""
    return HistoricSite.query.filter(
        HistoricSite.is_visible.is_(True),
        HistoricSite.pending_validation.is_(False),
        HistoricSite.deleted_at.is_(None),
    ).all()


def get_pending_historic_sites():
    """Obtiene todos los sitios históricos pendientes de validación y no eliminados."""
    return HistoricSite.query.filter(
        HistoricSite.pending_validation.is_(True), HistoricSite.deleted_at.is_(None)
    ).all()


def create_historic_site(**kwargs):
    """Crea un nuevo sitio histórico."""
    name = kwargs.get("name")
    brief_description = kwargs.get("brief_description")
    full_description = kwargs.get("full_description")
    inauguration_year = kwargs.get("inauguration_year")
    longitude = kwargs.get("longitude")
    latitude = kwargs.get("latitude")
    location = WKTElement(f"POINT({longitude} {latitude})", srid=4326)

    historic_site = HistoricSite(
        name=name,
        brief_description=brief_description,
        full_description=full_description,
        location=location,
        inauguration_year=inauguration_year,
    )
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
    historic_site, conservation_state, category, user, city, tags=None
):
    """Asigna relaciones a un sitio histórico."""

    historic_site.conservation_state = conservation_state
    historic_site.category = category
    historic_site.user = user
    historic_site.city = city
    if tags:
        for t in tags:
            historic_site.add_tag(t)
    db.session.commit()
    return historic_site


def update_conservation_state(site, conservation_id):
    """Actualiza el estado de conservación de un sitio histórico."""

    conservation_state = conservation_state_service.get_conservation_state_by_id(
        conservation_id
    )
    if not site.same_conservation_state(conservation_state):
        site.conservation_state = conservation_state
    return site


def update_category(site, category_id):
    """Actualiza la categoria de un sitio histórico."""

    category = category_service.get_category_by_id(category_id)
    if not site.same_category(category):
        site.category = category
    return site


def update_city(site, city_id):
    """Actualiza la ciudad de un sitio histórico."""

    city = city_service.get_city_by_id(city_id)
    if not site.same_city(city):
        site.city = city
    return site


def update_name(site, name):
    """Actualiza le nombre de un sitio histórico."""

    if not isinstance(name, str):
        raise ValueError("El nombre del sitio debe ser un string")
    if not site.same_name(name):
        site.name = name
    return site


def update_brief_description(site, description):
    """Actualiza la descripción breve de un sitio histórico."""

    if not isinstance(description, str):
        raise ValueError("La descripcion breve debe ser un string")
    if not site.same_brief_description(description):
        site.brief_description = description
    return site


def update_full_description(site, description):
    """Actualiza la descripción completa de un sitio histórico."""

    if not isinstance(description, str):
        raise ValueError("La descripcion completa debe ser un string")
    if not site.same_full_description(description):
        site.full_description = description
    return site


def update_location(site, location):
    """Actualiza la ubicación del sitio histórico solo si cambió realmente."""

    if not isinstance(location["lat"], (int, float)):
        raise ValueError("La latitude debe ser numerica")
    if not isinstance(location["lon"], (int, float)):
        raise ValueError("La longitude debe ser numerica")

    new_lat = float(location["lat"])
    new_lon = float(location["lon"])

    # Obtener coordenadas actuales
    current_lat = site.latitude
    current_lon = site.longitude

    # Solo actualizar si hay un cambio
    if current_lat != new_lat or current_lon != new_lon:
        site.location = WKTElement(f"POINT({new_lon} {new_lat})", srid=4326)

    return site


def update_inauguration_year(site, year):
    """Actualiza el año de inaguración de un sitio histórico."""

    if not site.same_inauguration_year(year):
        site.inauguration_year = year
    return site


def update_is_visible(site, visibility):
    """Actualiza el estado de visibilidad de un sitio histórico si no está borrado y está validado."""

    if not isinstance(visibility, bool):
        raise ValueError("El valor de visibilidad debe ser booleano")
    if visibility:
        if site.deleted_at:
            raise ValueError("El sitio no debe estar borrado")
        if site.pending_validation:
            raise ValueError("El sitio debe estar validado")
    if not site.same_visibility(visibility):
        site.is_visible = visibility
    return site


def update_tags(site, tag_ids):
    """Actualiza los tags de un sitio histórico."""

    tags = []
    for tag_id in tag_ids:
        tag = tag_service.get_tag_by_id(tag_id)
        if tag.deleted_at:
            raise ValueError("Se no se pueden asignar tags borrados")
        tags.append(tag)

    # Limpiar tags existentes y asignar nuevos usando métodos del modelo
    for tag in list(site.tags):
        site.remove_tag(tag)
    for tag in tags:
        site.add_tag(tag)


def validate_historic_site(site_id):
    """Valida un sitio histórico si no está borrado ni validado."""

    site = get_historic_site_by_id(site_id)
    if not site.pending_validation:
        raise ValueError(f"El sitio con id {site_id} ya se encuentra validado")
    if site.deleted_at:
        raise ValueError(f"El sitio con id {site_id} se encuentra borrado")
    site.pending_validation = False
    site.is_visible = True
    db.session.commit()
    return site


def assign_tags(site_id, tag_ids):
    """Asigna una lista de tags a un sitio histórico, reemplazando los existentes."""

    site = get_historic_site_by_id(site_id)

    update_tags(site, tag_ids)

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


def update_historic_site(body):
    """Actualiza todos los dados del sitio histórico.

    operations: Es un diccionario el cual es accedido por el cuerpo
    del parametro "body". Cada indice ejecuta la función de actilización
    para determinado campo del modelo HistoricSite.

    """
    try:
        site = get_historic_site_by_id(body["historic_site_id"])
        operations = {
            "name": update_name,
            "brief_description": update_brief_description,
            "full_description": update_full_description,
            "location": update_location,
            "inauguration_year": update_inauguration_year,
            "is_visible": update_is_visible,
            "city": update_city,
            "conservation_state": update_conservation_state,
            "category": update_category,
            "tags": update_tags,
        }

        for key, value in body.items():
            if key in operations:
                operations[key](site, value)
            elif key != "historic_site_id":
                raise ValueError("Campos invalidos enviados")

        site.update_at = datetime.now(timezone.utc)

        db.session.commit()
        return site
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error al editar el sitio histórico: {e}")


def restore_historic_site(site_id):
    """Restaura un sitio historico que se encontraba borrado."""

    site = get_historic_site_by_id(site_id)
    if not site.is_deleted:
        raise ValueError(f"El sitio {site_id} no se encuentra borrado")
    site.restore_site()
    db.session.commit()
    return site


def get_sites_filtered(
    filters=None,
    order_by: str = "name",
    sorted_by: str = "asc",
    paginate: bool = True,
    page: int = 1,
    per_page: int = 25,
    text_search_columns=None,
):
    """
    Devuelve sitios históricos filtrados, ordenados y opcionalmente paginados.
    Usa GenericSearchBuilder para filtros y paginate_query para paginación.

    Args:
        filters (dict): filtros a aplicar (ej: {"city_id": 1, "visible": True})
        order_by (str): columna para ordenar
        sorted_by (str): 'asc' o 'desc'
        paginate (bool): si True devuelve dict con paginación, si False lista completa
        page (int): número de página (si paginate=True)
        per_page (int): tamaño de página (si paginate=True)
        text_search_columns (list): columnas específicas para búsqueda de texto.
                                   Si es None, busca en TODAS las columnas de tipo texto.

    Returns:
        dict de paginación o lista de objetos HistoricSite
    """
    from core.models import City, Province

    filters = filters or {}

    # Si se filtra por ciudad, deducir automáticamente la provincia
    city_id = filters.get("city_id")
    if city_id:
        city = City.query.get(city_id)
        if not city:
            raise ValueError(f"No existe la ciudad con id {city_id}")
        # Añadir el province_id derivado, solo si no lo enviaron explícitamente
        filters.setdefault("province_id", city.province_id)

    # Construir la query base con el builder genérico
    # Si no se especifican columnas, busca en TODAS las columnas de tipo texto
    query = build_search_query(HistoricSite, filters, text_search_columns)

    # Aplicar join manual si se filtra por provincia (ya que el builder no maneja relaciones)
    province_id = filters.get("province_id")
    if province_id:
        query = (
            query.join(HistoricSite.city)
            .join(City.province)
            .filter(Province.id == province_id)
        )

    # Ordenar los resultados
    query = apply_ordering(query, HistoricSite, order_by, sorted_by)

    # Aplicar paginación o devolver lista completa
    if paginate:
        return paginate_query(
            query, page=page, per_page=per_page, order_by=order_by, sorted_by=sorted_by
        )
    return query.all()
