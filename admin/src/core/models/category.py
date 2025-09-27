from datetime import datetime, timezone

from core.database import db


class Category(db.Model):
    __tablename__ = "category"

    # Atributos
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)

    # Timestamps
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relaciones
    historic_sites = db.relationship("HistoricSite", back_populates="category")

    # Metodos
    def has_sites(self):
        """Indica si la categoria tiene sitios historicos asociados."""
        return len(self.historic_sites) > 0

    def can_be_deleted(self):
        """Indica si la categoria puede ser eliminada."""
        return not self.has_sites()

    def __repr__(self):
        return f"<Category {self.name}>"
