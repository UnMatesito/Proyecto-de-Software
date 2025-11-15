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


def approve_review(review_id: int) -> Review:
    """
    Aprueba una reseña.
    El event listener 'update_site_rating_after_flush' actualiza automáticamente
    el rating_count y average_rating del sitio histórico.
    """
    review = Review.query.get(review_id)
    if not review:
        raise ValueError(f"No existe review con id {review_id}")

    # Validar que la reseña esté pendiente
    if review.status == ReviewStatus.APROBADA:
        raise ValueError("La reseña ya está aprobada.")

    try:
        # Aprobar la reseña (cambia el status a APROBADA)
        review.approve()

        # Commit: aquí se dispara el event listener after_flush
        # que actualiza automáticamente rating_count y average_rating
        db.session.commit()

        # IMPORTANTE: Refrescar el sitio histórico para obtener los valores actualizados
        # No el review, sino el historic_site
        db.session.refresh(review.historic_site)

    except (ValueError, SQLAlchemyError) as e:
        db.session.rollback()
        raise RuntimeError(f"Error al aprobar la reseña: {e}")

    return review


def reject_review(review_id: int, reason: str) -> Review:
    """
    Rechaza una reseña con motivo.
    Si la reseña estaba previamente aprobada, el event listener
    actualizará automáticamente el rating del sitio.
    """
    review = Review.query.get(review_id)
    if not review:
        raise ValueError(f"No existe review con id {review_id}")

    if not reason or len(reason.strip()) < 5:
        raise ValueError("El motivo de rechazo debe tener al menos 5 caracteres.")
    if len(reason) > 255:
        raise ValueError("El motivo de rechazo no puede superar los 255 caracteres.")

    try:
        # Rechazar con motivo
        review.reject(reason)

        # Commit: el event listener se encarga de actualizar el rating si es necesario
        db.session.commit()

        # Refrescar el sitio histórico para obtener valores actualizados
        db.session.refresh(review.historic_site)

    except (ValueError, SQLAlchemyError) as e:
        db.session.rollback()
        raise RuntimeError(f"Error al rechazar la reseña: {e}")

    return review


def delete_review(review_id: int) -> bool:
    """
    Elimina definitivamente una reseña.
    Si estaba aprobada, el event listener actualiza el rating del sitio.
    """
    review = Review.query.get(review_id)
    if not review:
        raise ValueError(f"No existe review con id {review_id}")

    try:
        # Guardar referencia al sitio antes de eliminar
        historic_site = review.historic_site

        # Eliminar la reseña
        db.session.delete(review)
        db.session.commit()

        # Refrescar el sitio para obtener el rating actualizado
        db.session.refresh(historic_site)

    except (ValueError, SQLAlchemyError) as e:
        db.session.rollback()
        raise RuntimeError(f"Error al eliminar la reseña: {e}")

    return True


def update_review(review_id: int, rating: int = None, content: str = None) -> Review:
    """
    Actualiza una reseña existente (solo si está pendiente o aprobada).
    Si está aprobada y se cambia el rating, el event listener actualiza el sitio.
    """
    review = Review.query.get(review_id)
    if not review:
        raise ValueError(f"No existe review con id {review_id}")

    if review.status == ReviewStatus.RECHAZADA:
        raise ValueError("No se puede modificar una reseña rechazada.")

    try:
        if rating is not None:
            if not (1 <= rating <= 5):
                raise ValueError("La calificación debe estar entre 1 y 5.")
            review.rating = rating

        if content is not None:
            if not content.strip():
                raise ValueError("El contenido no puede estar vacío.")
            review.content = content.strip()

        # El event listener detectará el cambio de rating si la reseña está aprobada
        db.session.commit()
        db.session.refresh(review.historic_site)

    except (ValueError, SQLAlchemyError) as e:
        db.session.rollback()
        raise RuntimeError(f"Error al actualizar la reseña: {e}")

    return review


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
        try:
            filters["status"] = ReviewStatus(filters["status"].capitalize()).value
        except ValueError:
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


def get_review_by_id(review_id: int) -> Review:
    """Obtiene una review por su id con su sitio histórico cargado."""
    return Review.query.options(joinedload(Review.historic_site)).get(review_id)


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


def get_site_reviews(
    site_id: int, status: ReviewStatus = None, page: int = 1, per_page: int = 25
):
    """
    Obtiene las reseñas de un sitio histórico específico.
    Útil para mostrar reseñas aprobadas en la página del sitio.
    """
    query = Review.query.options(joinedload(Review.user)).filter_by(
        historic_site_id=site_id
    )

    if status:
        query = query.filter_by(status=status)

    query = query.order_by(Review.created_at.desc())

    return query.paginate(page=page, per_page=per_page, error_out=False)
