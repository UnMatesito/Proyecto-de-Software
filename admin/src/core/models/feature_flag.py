from datetime import datetime, timezone

from core.database import db


class FeatureFlag(db.Model):
    __tablename__ = "feature_flag"

    # Atributos
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)
    description = db.Column(db.String(255), nullable=False)
    is_enabled = db.Column(db.Boolean, nullable=False)
    maintenance_message = db.Column(db.String(300), nullable=False)

    # Timestamps
    last_modified_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relaciones
    last_modified_by = db.relationship("User")
    last_modified_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    # Metodos
    def enable(self, user_id, message=""):
        """Habilita la feature flag."""
        self.is_enabled = True
        self.last_modified_at = datetime.now(timezone.utc)
        self.last_modified_by_id = user_id
        if message:
            self.maintenance_message = message

    def disable(self, user_id):
        """Deshabilita la feature flag."""
        self.is_enabled = False
        self.last_modified_at = datetime.now(timezone.utc)
        self.last_modified_by_id = user_id

    def is_maintenance(self):
        return  self.name in ["admin_maintenance_mode", "portal_maintenance_mode"]

    def __repr__(self):
        return f"<Feature_flag {self.name}>"
