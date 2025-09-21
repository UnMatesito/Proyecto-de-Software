from core.database import db
from core.models import Tag
from core.utils import pagination
from sqlalchemy import desc  

def get_tag_by_id(tag_id):
    tag = Tag.query.get(tag_id)
    if (not tag):
        raise ValueError(f"No existe un tag con id {tag_id}")
    return tag

def get_tag_by_name(tag_name):
    tag = Tag.query.filter_by(Tag.name == tag_name)
    if (not tag):
        raise ValueError(f"No existe un tag con nombre {tag_name}")
    return tag
    

def validation_tag_name(tag_name):
    if (len(tag_name) > 50):
        raise ValueError("El tamaño maximo para un nombre es de caracteres es 50")
    if (len(tag_name) < 3):
        raise ValueError("El tamaño minimo para un nombre es de caracteres es 3")
    tag_name = tag_name.lower()
    tag = get_tag_by_name(tag_name)
    if (tag):
        raise ValueError("Ya existe un tag con nombre {tag_name}")
    return True

def create_tag(name):    
    if (not name):
        raise ValueError("El nombre del tag es obligatorio")
    validation_tag_name(name)
    tag = Tag(name)
    db.session.add(tag)
    db.session.commit()
    return tag

def get_paginated_tags(page, order):
    if (order == "asc"):
        query = Tag.query.order_by(Tag.created_at)
    else:
        query = Tag.query.order_by(desc(Tag.name))
    return pagination.paginate_query(query, page = page)
