from core.database import db
from core.models import City


def get_city_by_id(city_id):
    city = City.query.get(city_id)
    if not city:
        raise ValueError(f"No existe la ciudad con id {city_id}")
    return city
