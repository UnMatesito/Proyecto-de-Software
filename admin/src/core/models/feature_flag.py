from datetime import datetime, timezone

from core.database import db


class Feature_flag(db.Model):
    __tablename__ = "feature_flag"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=False, unique=True)
    is_enabled = db.Column(db.Boolean, nullable=False)
    maintenance_message = db.Column(db.String(300), nullable=False)
    last_modified_at = db.Column(
        db.DateTime, default=lambda: DateTime.now(timezone.utc)
    )
    last_modified_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    last_modified_by = db.relationship("User")
    inserted_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    created_at = db.Column(db.DateTime, default=lambda: DateTime.now(timezone.utc))

    def __repr__(self):
        return f"<Feature_flag {self.name}>"
