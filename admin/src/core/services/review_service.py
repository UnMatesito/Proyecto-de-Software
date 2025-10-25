from sqlalchemy.exc import IntegrityError

from core.database import db
from core.models.review import Review, ReviewStatus
from core.utils.pagination import paginate_query
from core.utils.search import build_search_query, apply_ordering


def create_review(user_id: int, site_id: int, rating: int, content: str) -> Review:
    """Crea una nueva reseña pendiente de aprobación."""
    existing = Review.query.filter_by(user_id=user_id, historic_site_id=site_id).first()

    if existing:
        raise ValueError("El usuario ya dejó una reseña para este sitio.")
    if not (1 <= rating <= 5):
        raise ValueError("La calificación debe estar entre 1 y 5.")
    if not content.strip():
        raise ValueError("El contenido de la reseña no puede estar vacío.")

    review = Review(
        user_id=user_id,
        historic_site_id=site_id,
        rating=rating,
        content=content.strip(),
        status=ReviewStatus.PENDIENTE,
    )
    try:
        db.session.add(review)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()

        msg = str(e.orig)
        if "unique_user_review" in msg:
            raise ValueError("El usuario ya dejó una reseña para este sitio.")
        elif "check_rating_range" in msg:
            raise ValueError("La calificación debe estar entre 1 y 5.")
        else:
            raise ValueError("No se pudo crear la reseña. Verifique los datos ingresados.")

    return review


def approve_review(review_id: int) -> bool:
    """Aprueba una reseña."""
    review = Review.query.get(review_id)
    if not review:
        return False
    review.approve()
    db.session.commit()
    return True


def reject_review(review_id: int, reason: str) -> bool:
    """Rechaza una reseña con motivo."""
    review = Review.query.get(review_id)
    if not review:
        return False
    review.reject(reason)
    db.session.commit()
    return True


def delete_review(review_id: int) -> bool:
    """Elimina definitivamente una reseña."""
    review = Review.query.get(review_id)
    if not review:
        return False
    db.session.delete(review)
    db.session.commit()
    return True

def get_paginated_reviews(filters=None, page=1, per_page=25, order_by="created_at", order_dir="asc"):
    """
    Obtiene reseñas con filtros combinables y paginación.
    Filtros soportados:
      - status: 'Pendiente', 'Aprobada', 'Rechazada'
      - site_id: ID del sitio histórico
      - user_id: ID del usuario
      - rating_min / rating_max
      - date_from / date_to (YYYY-MM-DD)
      - search_text: busca en el contenido
    """
    filters = filters or {}

    # Normalizar enum si llega como texto
    if "status" in filters and filters["status"]:
        try:
            filters["status"] = ReviewStatus(filters["status"].capitalize())
        except ValueError:
            filters.pop("status", None)

    # Construir query de búsqueda flexible
    query = build_search_query(Review, filters, text_search_columns=["content"])

    # Filtros adicionales de rango de calificación
    if "rating_min" in filters:
        query = query.filter(Review.rating >= int(filters["rating_min"]))
    if "rating_max" in filters:
        query = query.filter(Review.rating <= int(filters["rating_max"]))

    # Ordenar resultados
    query = apply_ordering(query, Review, order_by, order_dir)

    # Retornar resultados paginados
    return paginate_query(query, page, per_page, order_by=order_by, sorted_by=order_dir)
