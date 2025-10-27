import enum
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, event

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
    )

    # Validaciones
    @db.validates("rating")
    def validate_rating(self, key, value):
        if not 1 <= value <= 5:
            raise ValueError("La calificación debe estar entre 1 y 5.")
        return value

    # Métodos
    def approve(self):
        """Aprueba la reseña."""
        self.status = ReviewStatus.APROBADA
        self.rejected_reason = None

    def reject(self, reason: str):
        """Rechaza la reseña con motivo."""
        self.status = ReviewStatus.RECHAZADA
        self.rejected_reason = reason[:200] if reason else None

    def is_pending(self):
        return self.status.value == "Pendiente"

    def is_approved(self):
        return self.status.value == "Aprobada"

    def is_rejected(self):
        return self.status.value == "Rechazada"

    def __repr__(self):
        return f"<Review {self.id} - {self.status}>"


@event.listens_for(Review, "after_insert")
def add_site_rating(mapper, connection, target):
    from core.models import HistoricSite

    if target.status == ReviewStatus.APROBADA:
        session = db.object_session(target)
        site = session.get(HistoricSite, target.historic_site_id)
        if site:
            site.add_rating(target.rating)


@event.listens_for(Review, "after_update")
def update_site_rating(mapper, connection, target):
    from core.models import HistoricSite

    session = db.object_session(target)
    site = session.get(HistoricSite, target.historic_site_id)
    if not site:
        return

    # Detectar cambios en rating o estado
    history = db.inspect(target).attrs.rating.history
    status_history = db.inspect(target).attrs.status.history

    # Caso 1: rating cambió (sigue aprobada)
    if history.has_changes() and target.status == ReviewStatus.APROBADA:
        old = history.deleted[0] if history.deleted else None
        if old is not None:
            site.update_rating(old, target.rating)

    # Caso 2: pasó a Aprobada
    elif status_history.has_changes() and target.status == ReviewStatus.APROBADA:
        site.add_rating(target.rating)

    # Caso 3: pasó de Aprobada a Rechazada o Pendiente
    elif (
        status_history.has_changes()
        and status_history.deleted
        and status_history.deleted[0] == ReviewStatus.APROBADA
    ):
        site.remove_rating(target.rating)


@event.listens_for(Review, "after_delete")
def remove_site_rating(mapper, connection, target):
    from core.models import HistoricSite

    if target.status == ReviewStatus.APROBADA:
        session = db.object_session(target)
        site = session.get(HistoricSite, target.historic_site_id)
        if site:
            site.remove_rating(target.rating)
