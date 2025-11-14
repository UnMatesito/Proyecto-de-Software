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
    Actualiza rating_count, rating_total y rating_avg de HistoricSite
    después de que SQLAlchemy termina el flush.
    Maneja inserts, updates y deletes sin inner-flush warnings.
    """
    from core.models import Review, HistoricSite

    # agregar rating si la review está aprobada
    for obj in session.new:
        if isinstance(obj, Review):
            if obj.status == ReviewStatus.APROBADA:
                site = session.get(HistoricSite, obj.historic_site_id)
                if site:
                    site.add_rating(obj.rating)

    # manejar cambios en rating o status
    for obj in session.dirty:
        if isinstance(obj, Review):
            state = db.inspect(obj)

            site = session.get(HistoricSite, obj.historic_site_id)
            if not site:
                continue

            rating_hist = state.attrs.rating.history
            status_hist = state.attrs.status.history

            # Rating cambió y sigue aprobada
            if rating_hist.has_changes() and obj.status == ReviewStatus.APROBADA:
                old = rating_hist.deleted[0] if rating_hist.deleted else None
                if old is not None:
                    site.update_rating(old, obj.rating)

            # Cambió status y ahora está aprobada
            if status_hist.has_changes() and obj.status == ReviewStatus.APROBADA:
                site.add_rating(obj.rating)

            # Cambió status y dejó de estar aprobada
            if (
                status_hist.has_changes()
                and status_hist.deleted
                and status_hist.deleted[0] == ReviewStatus.APROBADA
            ):
                site.remove_rating(obj.rating)

    # si la review era aprobada, restar rating
    for obj in session.deleted:
        if isinstance(obj, Review):
            if obj.status == ReviewStatus.APROBADA:
                site = session.get(HistoricSite, obj.historic_site_id)
                if site:
                    site.remove_rating(obj.rating)