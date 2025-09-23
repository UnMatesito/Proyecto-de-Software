from core.database import db
from core.models import City


def get_all_cities():
    """Obtiene todas las ciudades."""
    return City.query.all()


def get_city_by_province(province_id):
    """Obtiene todas las ciudades de una provincia dada su id."""
    return City.query.filter_by(province_id=province_id).all()


def get_city_by_id(city_id):
    """Obtiene una ciudad por su id."""
    city = City.query.get(city_id)
    if not city:
        raise ValueError(f"No existe la ciudad con id {city_id}")
    return city


def create_city(name, province_id):
    """Crea una nueva ciudad."""
    city = City(name=name, province_id=province_id)
    db.session.add(city)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Error al crear la ciudad: {e}")
    return city
