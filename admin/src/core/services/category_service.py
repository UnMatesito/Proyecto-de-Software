from core.models import Category


def get_all_categories():
    """Obtiene todas las categorías"""
    return Category.query.all()


def get_category_by_id(category_id):
    """Obtiene una categoría por su ID."""
    category = Category.query.get(category_id)
    if not category:
        raise ValueError(f"No existe la categoria con el id {category_id}")
    return category
