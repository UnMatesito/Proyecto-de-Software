from core.database import db
from core.models import CategorySite

def get_category_site_by_id(category_id):
    category = CategorySite.query.get(category_id)
    if (not category):
        raise ValueError(f"No existe la cetegoria con el id {category_id}")
    return category