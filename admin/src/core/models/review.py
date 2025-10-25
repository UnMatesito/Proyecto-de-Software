from datetime import datetime, timezone

from sqlalchemy import CheckConstraint

from core.database import db
import enum

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
        nullable=False
    )
    rejected_reason = db.Column(db.String(200), nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relaciones
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    user = db.relationship("User", backref="reviews")

    historic_site_id = db.Column(
        db.Integer, db.ForeignKey("historic_site.id", ondelete="CASCADE"), nullable=False
    )
    historic_site = db.relationship("HistoricSite", backref="reviews")

    # Restricciones
    __table_args__ = (
        db.UniqueConstraint("user_id", "historic_site_id", name="unique_user_review"), # Un usuario solo puede dejar una reseña por sitio histórico
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"), # La calificación debe estar entre 1 y 5
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
