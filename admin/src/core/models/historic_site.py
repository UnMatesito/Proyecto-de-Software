from datetime import datetime, timezone

from core.database import db

historic_site_tag = db.Table(
    "historic_site_tag",
    db.Column(
        "historic_site_id",
        db.Integer,
        db.ForeignKey("historic_site.id"),
        primary_key=True,
    ),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
)


class HistoricSite(db.Model):
    __tablename__ = "historic_site"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    brief_description = db.Column(db.String, nullable=False)
    full_description = db.Column(db.String, nullable=False)
    latitude = db.Column(db.Double, nullable=False)
    longitude = db.Column(db.Double, nullable=False)
    inauguration_year = db.Column(db.Integer, nullable=False)
    registration_date = db.Column(db.DateTime, nullable=False)
    is_visible = db.Column(db.Boolean, default=False, nullable=False)
    pending_validation = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    deleted_at = db.Column(db.DateTime, default=None, nullable=True)

    city_id = db.Column(db.Integer, db.ForeignKey("city.id"))
    city = db.relationship("City", back_populates="historic_sites")

    conservation_state_id = db.Column(
        db.Integer, db.ForeignKey("conservation_state.id")
    )
    conservation_state = db.relationship(
        "ConservationState", back_populates="historic_sites"
    )

    category_id = db.Column(db.Integer, db.ForeignKey("category_site.id"))
    category_site = db.relationship("Category", back_populates="historic_sites")

    proposed_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="historic_sites")

    def __repr__(self):
        return f"<Historic Site {self.name}>"
