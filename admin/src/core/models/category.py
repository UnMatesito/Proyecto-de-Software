from datetime import datetime, timezone

from core.database import db

category_site = db.Table(
    "category_site",
    db.Column(
        "historic_site_id",
        db.Integer,
        db.ForeignKey("historic_site.id"),
        primary_key=True,
    ),
    db.Column(
        "category_id", db.Integer, db.ForeignKey("category.id"), primary_key=True
    ),
)


class Category(db.Model):
    __tablename__ = "category"

    # Atributos
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.String(255), nullable=False)

    # Timestamps
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relaciones
    historic_sites = db.relationship(
        "HistoricSite", secondary=category_site, back_populates="categories"
    )

    # Metodos
    def has_sites(self):
        """Indica si la categoria tiene sitios historicos asociados."""
        return len(self.historic_sites) > 0

    def can_be_deleted(self):
        """Indica si la categoria puede ser eliminada."""
        return not self.has_sites()

    def __repr__(self):
        return f"<Category {self.name}>"
