from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import joinedload

from core.database import db
from core.models.review import Review, ReviewStatus
from core.services.user_service import get_user_by_email
from core.utils.pagination import paginate_query
from core.utils.search import apply_ordering, build_search_query


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
            raise ValueError(
                "No se pudo crear la reseña. Verifique los datos ingresados."
            )

    return review


def approve_review(review_id: int) -> bool:
    """Aprueba una reseña."""
    review = Review.query.get(review_id)
    if not review:
        raise ValueError(f"No existe review con id {review_id}")
    try:
        review.approve()
        db.session.commit()
        db.session.refresh(review)
    except (ValueError, SQLAlchemyError) as e:
        db.session.rollback()
        raise RuntimeError(f"Error al aprobar la reseña {e}")
    return True


def reject_review(review_id: int, reason: str) -> bool:
    """Rechaza una reseña con motivo."""
    review = Review.query.get(review_id)
    if not review:
        raise ValueError(f"No existe review con id {review_id}")
    if not reason or len(reason.strip()) < 5:
        raise ValueError("El motivo de rechazo debe tener al menos 5 caracteres.")
    if len(reason) > 255:
        raise ValueError("El motivo de rechazo no puede superar los 255 caracteres.")
    try:
        review.reject(reason)
        db.session.commit()
        db.session.refresh(review)
    except (ValueError, SQLAlchemyError) as e:
        db.session.rollback()
        raise RuntimeError(f"Error al aprobar la reseña {e}")
    return True


def delete_review(review_id: int):
    """Elimina definitivamente una reseña."""
    review = Review.query.get(review_id)
    if not review:
        raise ValueError(f"No existe review con id {review_id}")
    try:
        db.session.delete(review)
        db.session.commit()
    except (ValueError, SQLAlchemyError) as e:
        db.session.rollback()
        raise RuntimeError(f"Error al eliminar la reseña: {e}")
    return True


def get_paginated_reviews(
    filters=None, page=1, per_page=25, order_by="created_at", order_dir="asc"
):
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
    query = Review.query
    filters = filters or {}

    # Normalizar enum si llega como texto
    if "status" in filters and filters["status"]:
        value = filters["status"]

        # si ya viene un enum dejarlo como está
        if isinstance(value, ReviewStatus):
            pass

        # si viene como string convertir a Enum
        elif isinstance(value, str):
            try:
                filters["status"] = ReviewStatus(value.capitalize())
            except ValueError:
                filters.pop("status", None)

        # si es un valor desconocido eliminar el filtro
        else:
            filters.pop("status", None)

    if "search_text" in filters and filters["search_text"]:
        text = filters["search_text"].strip()

        # Si parece un mail busco por usuario
        if "@" in text and "." in text:
            user = get_user_by_email(text)
            if user:
                filters["user_id"] = user.id
            filters.pop("search_text", None)

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


def get_review_by_id(review_id):
    """Obtiene una review por su id."""
    return Review.query.get(review_id)


def get_user_reviews(
    user_id: int, page: int = 1, per_page: int = 25, sort: str = "date_desc"
):
    """Obtiene las reseñas de un usuario con la paginación solicitada."""

    try:
        per_page = int(per_page)
    except (TypeError, ValueError):
        per_page = 25

    if per_page not in {25, 50, 100}:
        per_page = 25

    if page is None or page < 1:
        page = 1

    sort = sort or "date_desc"

    query = Review.query.options(joinedload(Review.historic_site)).filter_by(
        user_id=user_id
    )

    if sort == "date_asc":
        query = query.order_by(Review.created_at.asc())
    else:
        query = query.order_by(Review.created_at.desc())

    return query.paginate(page=page, per_page=per_page, error_out=False)
