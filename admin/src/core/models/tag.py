from datetime import datetime, timezone

from core.database import db
from core.models.historic_site import historic_site_tag


class Tag(db.Model):
    __tablename__ = "tag"

    # Atributos
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column("name", db.String(50), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(50), unique=True, nullable=False, index=True)

    # Timestamps
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    deleted_at = db.Column(db.DateTime, default=None)

    # Relaciones
    sites = db.relationship(
        "HistoricSite", secondary=historic_site_tag, back_populates="tags"
    )

    # Metodos
    def has_sites(self):
        """Retorna verdadero si el tag está asociado a uno o más sitios históricos."""

        return len(self.sites) > 0

    def delete_tag(self):
        """Elimina el tag setteando el campo "deleted_at" con la fecha actual."""

        self.deleted_at = datetime.now(timezone.utc)

    def restore_tag(self):
        """Restaura el tag eliminiado."""

        self.deleted_at = None

    def is_deleted(self):
        """Retorna verdadero si el tag está eliminado."""

        return self.deleted_at is not None

    def is_active(self):
        """Retorna verdadero si el tag no está eliminado."""

        return self.deleted_at is None

    def can_be_deleted(self):
        """Retorna verdadero si el tag no posee sitios históricos asociados."""

        return not self.has_sites()

    def __repr__(self):
        """Retorna una representación del tag el cual posee su nombre."""

        return f"<Tag {self.name}>"
