from core.database import db
from core.models import Province


def get_all_provinces():
    """Obtiene todas las provincias de la base de datos."""
    return Province.query.all()


def get_province_by_id(province_id):
    """Obtiene una provincia por su ID."""
    return Province.query.get(province_id)


def create_province(name):
    """Crea una nueva provincia."""
    if Province.query.filter_by(name=name).first():
        raise ValueError("Ya existe una provincia con ese nombre")

    province = Province(name=name)
    db.session.add(province)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Error al crear la provincia: {e}")
    return province
