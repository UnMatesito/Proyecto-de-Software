import enum
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, event
from sqlalchemy.orm import Session, attributes

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
    Actualiza rating_count, rating_total y average_rating de HistoricSite
    después de flush.
    Maneja inserts, updates, deletes y cambios de sitio sin inner-flush.
    """
    from core.models import Review, HistoricSite, ReviewStatus
    import sqlalchemy as sa

    def commit_rating_fields(site):
        attributes.set_committed_value(site, "rating_total", site.rating_total)
        attributes.set_committed_value(site, "rating_count", site.rating_count)
        attributes.set_committed_value(site, "average_rating", site.average_rating)

    for obj in session.new:
        if isinstance(obj, Review) and obj.status == ReviewStatus.APROBADA:
            site = session.get(HistoricSite, obj.historic_site_id)
            if site:
                site.add_rating(obj.rating)
                commit_rating_fields(site)

    for obj in session.dirty:
        if not isinstance(obj, Review):
            continue

        state = sa.inspect(obj)

        new_site = session.get(HistoricSite, obj.historic_site_id)
        old_site_id = (
            state.attrs.historic_site_id.history.deleted[0]
            if state.attrs.historic_site_id.history.deleted
            else obj.historic_site_id
        )
        old_site = session.get(HistoricSite, old_site_id)

        old_rating = (
            state.attrs.rating.history.deleted[0]
            if state.attrs.rating.history.deleted
            else None
        )
        new_rating = obj.rating

        old_status = (
            state.attrs.status.history.deleted[0]
            if state.attrs.status.history.deleted
            else None
        )
        new_status = obj.status

        if state.attrs.historic_site_id.history.has_changes():
            if old_status == ReviewStatus.APROBADA and old_site:
                old_site.remove_rating(old_rating)
                commit_rating_fields(old_site)

            if new_status == ReviewStatus.APROBADA and new_site:
                new_site.add_rating(new_rating)
                commit_rating_fields(new_site)

            continue

        if old_rating is not None and old_rating != new_rating:
            if new_status == ReviewStatus.APROBADA and new_site:
                new_site.update_rating(old_rating, new_rating)
                commit_rating_fields(new_site)

        if old_status != new_status:
            if new_status == ReviewStatus.APROBADA and new_site:
                new_site.add_rating(new_rating)
                commit_rating_fields(new_site)

            if old_status == ReviewStatus.APROBADA and new_site:
                new_site.remove_rating(old_rating or new_rating)
                commit_rating_fields(new_site)

    for obj in session.deleted:
        if isinstance(obj, Review) and obj.status == ReviewStatus.APROBADA:
            site = session.get(HistoricSite, obj.historic_site_id)
            if site:
                site.remove_rating(obj.rating)
                commit_rating_fields(site)