from core.database import db
from core.models import Province


def list_provinces():
    return Province.query.all()
