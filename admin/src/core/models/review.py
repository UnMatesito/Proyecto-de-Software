import enum
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, event
from sqlalchemy.orm import Session

from core.database import db


class ReviewStatus(enum.Enum):
    PENDIENTE = "Pendiente"
    APROBADA = "Aprobada"
    RECHAZADA = "Rechazada"


class Review(db.Model):
    __tablename__ = "review"

    id = db.Column(db.Integer, primary_key=True)

    rating = db.Column(db.SmallInteger, nullable=False)
    content = db.Column(db.Text, nullable=False)

    status = db.Column(
        db.Enum(ReviewStatus, name="review_status_enum", native_enum=False),
        default=ReviewStatus.PENDIENTE,
        nullable=False,
    )

    rejected_reason = db.Column(db.String(200), nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relaciones
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    user = db.relationship("User", backref="reviews")

    historic_site_id = db.Column(
        db.Integer,
        db.ForeignKey("historic_site.id", ondelete="CASCADE"),
        nullable=False,
    )
    historic_site = db.relationship("HistoricSite", back_populates="reviews")

    # Restricciones
    __table_args__ = (
        db.UniqueConstraint(
            "user_id", "historic_site_id", name="unique_user_review"
        ),  # Un usuario solo puede dejar una reseña por sitio histórico
        CheckConstraint(
            "rating >= 1 AND rating <= 5", name="check_rating_range"
        ),  # La calificación debe estar entre 1 y 5
        db.Index(
            "idx_historic_site_rating", "rating"
        ),  # Índice para optimizar consultas por calificación
    )

    # Validaciones
    @db.validates("rating")
    def validate_rating(self, key, value):
        if value is None:
            raise ValueError("La calificación no puede ser nula.")
        if not 1 <= int(value) <= 5:
            raise ValueError("La calificación debe estar entre 1 y 5.")
        return int(value)

    @db.validates("content")
    def validate_content(self, key, value):
        if not value or not value.strip():
            raise ValueError("El contenido de la reseña no puede estar vacío.")
        return value.strip()

    # Métodos
    def approve(self):
        """Aprueba la reseña."""
        self.status = ReviewStatus.APROBADA
        self.rejected_reason = None

    def reject(self, reason: str):
        """Rechaza la reseña con motivo."""
        if not reason or len(reason.strip()) < 5:
            raise ValueError("El motivo de rechazo debe tener al menos 5 caracteres.")
        self.status = ReviewStatus.RECHAZADA
        self.rejected_reason = reason.strip()[:200]

    def is_pending(self):
        return self.status == ReviewStatus.PENDIENTE

    def is_approved(self):
        return self.status == ReviewStatus.APROBADA

    def is_rejected(self):
        return self.status == ReviewStatus.RECHAZADA

    def __repr__(self):
        return f"<Review {self.id} - {self.status.value}>"


@event.listens_for(Session, "after_flush")
def update_site_rating_after_flush(session, ctx):
    """
    Actualiza rating_count y average_rating de HistoricSite después de flush.
    Maneja inserts, updates, deletes y cambios de sitio sin inner-flush.
    """
    from core.models import Review, HistoricSite, ReviewStatus
    import sqlalchemy as sa

    def as_status(value):
        """Convierte el valor a ReviewStatus de forma segura."""
        if value is None:
            return None
        if isinstance(value, ReviewStatus):
            return value
        try:
            return ReviewStatus(value)
        except (ValueError, TypeError):
            return None

    def track_site(site_id):
        """Marca un sitio para actualización."""
        if site_id is not None:
            affected_site_ids.add(site_id)

    affected_site_ids = set()

    # Procesar nuevas reseñas aprobadas
    for obj in session.new:
        if isinstance(obj, Review) and as_status(obj.status) == ReviewStatus.APROBADA:
            track_site(obj.historic_site_id)

    # Procesar reseñas modificadas
    for obj in session.dirty:
        if not isinstance(obj, Review):
            continue

        state = sa.inspect(obj)

        # Obtener el sitio anterior
        old_site_id = (
            state.attrs.historic_site_id.history.deleted[0]
            if state.attrs.historic_site_id.history.deleted
            else obj.historic_site_id
        )

        # Obtener estados anterior y nuevo
        old_status = (
            as_status(state.attrs.status.history.deleted[0])
            if state.attrs.status.history.deleted
            else as_status(obj.status)
        )
        new_status = as_status(obj.status)

        # Verificar cambios
        moved_site = state.attrs.historic_site_id.history.has_changes()
        rating_changed = state.attrs.rating.history.has_changes()

        # Si se movió a otro sitio
        if moved_site:
            if old_status == ReviewStatus.APROBADA:
                track_site(old_site_id)
            if new_status == ReviewStatus.APROBADA:
                track_site(obj.historic_site_id)

        # Si cambió el estado
        if old_status != new_status:
            if old_status == ReviewStatus.APROBADA:
                track_site(old_site_id)
            if new_status == ReviewStatus.APROBADA:
                track_site(obj.historic_site_id)
        # Si cambió el rating de una reseña aprobada
        elif new_status == ReviewStatus.APROBADA and rating_changed:
            track_site(obj.historic_site_id)

    # Procesar reseñas eliminadas
    for obj in session.deleted:
        if isinstance(obj, Review) and as_status(obj.status) == ReviewStatus.APROBADA:
            track_site(obj.historic_site_id)

    # Si no hay sitios afectados, salir
    if not affected_site_ids:
        return

    site_ids = [site_id for site_id in affected_site_ids if site_id is not None]

    if not site_ids:
        return

    # Usar el enum directamente, no el valor string
    stmt = (
        sa.select(
            Review.historic_site_id,
            sa.func.count(Review.id),
            sa.func.coalesce(sa.func.avg(Review.rating), 0.0),
        )
        .where(
            Review.historic_site_id.in_(site_ids),
            Review.status == ReviewStatus.APROBADA,
        )
        .group_by(Review.historic_site_id)
    )

    # Inicializar agregados con 0
    aggregates = {site_id: (0, 0.0) for site_id in site_ids}

    # Ejecutar query y llenar agregados
    for site_id, count, avg in session.execute(stmt):
        aggregates[site_id] = (int(count or 0), float(avg or 0.0))

    # Actualizar cada sitio
    for site_id, (count, avg) in aggregates.items():
        session.execute(
            sa.update(HistoricSite)
            .where(HistoricSite.id == site_id)
            .values(
                rating_count=count,
                average_rating=avg if count else 0.0,
            )
        )

    # Expirar los atributos en caché para forzar recarga
    mapper = sa.inspect(HistoricSite)
    for site_id in site_ids:
        identity_key = mapper.identity_key_from_primary_key((site_id,))
        site = session.identity_map.get(identity_key)
        if site is not None:
            session.expire(site, ["rating_count", "average_rating"])