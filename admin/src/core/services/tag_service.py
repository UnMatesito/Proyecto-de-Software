from datetime import datetime, timezone

from slugify import slugify
from sqlalchemy import desc, func
from sqlalchemy.exc import SQLAlchemyError

from core.database import db
from core.models import Tag
from core.utils import pagination


def get_all_not_deleted_tags():
    """Obtiene todos los tags no borrados."""

    return Tag.query.filter_by(deleted_at=None).all()


def get_all_tags():
    """Obtiene todos los tags."""

    return Tag.query.all()


def get_tag_by_id(tag_id):
    """Obtiene un tag por su id."""

    tag = Tag.query.get(tag_id)
    if not tag:
        raise ValueError(f"No existe un tag con id {tag_id}")
    return tag


def get_tag_by_name(tag_name):
    """Obtiene un tag por su nombre."""

    tag = Tag.query.filter_by(name=tag_name).first()
    if not tag:
        raise ValueError(f"No existe un tag con nombre {tag_name}")
    return tag


def tag_exist(tag_name):
    """Retorna verdadero o falso si un tag existe por su nombre."""

    return (
            db.session.query(Tag.id)
            .filter(func.lower(Tag.name) == func.lower(tag_name))
            .first()
            is not None
    )

def slug_exist(slug):
    """Retorna verdadero o falso si un tag existe por su slug."""

    return (
            db.session.query(Tag.id)
            .filter(func.lower(Tag.slug) == func.lower(slug))
            .first()
            is not None
    )

def validate_tag_name(tag_name):
    """Valida el nombre de un posible futuro tag."""

    if len(tag_name) > 50:
        raise ValueError("El tamaño maximo para un nombre es de caracteres es 50")
    if len(tag_name) < 3:
        raise ValueError("El tamaño minimo para un nombre es de caracteres es 3")
    if tag_exist(tag_name):
        raise ValueError(f"Ya existe un tag con nombre: {tag_name}")


def validate_tag_slug(slug):
    """Valida el slug de un posible futuro tag."""

    if slug_exist(slug=slug):
        raise ValueError(f"Ya existe un tag con el slug: {slug}")


def create_tag(name):
    """Crea un nuevo tag si las validaciones de su nombre y slug son correctas."""

    if not name:
        raise ValueError("El nombre del tag es obligatorio")
    name = str(name).strip()
    slug = slugify(name)
    validate_tag_name(name)
    validate_tag_slug(slug)
    tag = Tag(name=name, slug=slug)
    db.session.add(tag)
    db.session.commit()
    return tag


def update_tag(tag_id, new_name):
    """Actualiza el nombre de un tag."""

    tag = get_tag_by_id(tag_id)

    if tag.is_deleted():
        raise ValueError("No se puede actualizar un tag eliminado")

    new_name = new_name.strip()
    slug = slugify(new_name)
    validate_tag_name(new_name)
    validate_tag_slug(slug)

    try:
        tag.name = new_name
        tag.slug = slug
        db.session.commit()
        return tag

    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error al actualizar el tag: {e}")


def get_paginated_tags(page=1, order_by="name", sorted_by="asc", name=None):
    """Retorna el formato paginado de los tags,
    el cual puede estar ordenado por nombre o fecha de creación
    y de manera ascendente o descendente."""
    query = Tag.query
    if name:
        query = query.filter_by(name=name)
    if order_by == "name":
        if sorted_by == "asc":
            query = query.order_by(Tag.name)
        else:
            query = query.order_by(desc(Tag.name))
    elif order_by == "created_at":
        if sorted_by == "asc":
            query = query.order_by(Tag.created_at)
        else:
            query = query.order_by(desc(Tag.created_at))

    return pagination.paginate_query(
        query, page=page, order_by=order_by, sorted_by=sorted_by
    )


def delete_tag(tag_id):
    """Borra un tag (encontrado por su id) asignando la fecha actual como fecha de borrado."""

    tag = get_tag_by_id(tag_id)
    if tag.is_deleted():
        raise ValueError("El tag se encuentra borrado")
    if tag.has_sites():
        raise ValueError("No se puede eliminar el tag porque está asociado a uno o más sitios históricos.")
    tag.deleted_at = datetime.now(timezone.utc)
    db.session.commit()
    return tag
