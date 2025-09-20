from core.database import db
from datetime import datetime, timezone

class HistoricSite(db.Model):
    __tablename__ = "historic_site"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255), nullable = False)
    brief_description = db.Column(db.String, nullable = False)
    full_description = db.Column(db.String, nullable = False)
    latitude = db.Column(db.Double, nullable = False)
    longitude = db.Column(db.Double, nullable = False)
    inauguration_year = db.Column(db.Integer, nullable = False)
    registration_date = db.Column (db.DateTime, nullable = False)
    is_visible = db.Column (db.Boolean, default = False , nullable = False)
    pending_validation = db.Column (db.Boolean, default = True, nullable = False)
    created_at = db.Column (
        db.DateTime,
        default = lambda: datetime.now(timezone.utc),
        nullable = False
    )
    updated_at = db.Column (
        db.DateTime,
        default = lambda: datetime.now(timezone.utc),
        nullable = False
    )
    deleted_at = db.Column (
        db.DateTime,
        default = None,
        nullable = True
    )
    city_id = 