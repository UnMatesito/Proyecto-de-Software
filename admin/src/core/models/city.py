from datetime import datetime, timezone

from core.database import db


class City(db.Model):
    __tablename__ = "city"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)

    province_id = db.Column(db.Integer, db.ForeignKey("province.id"))
    province = db.relationship("Province", back_populates="cities")

    historic_sites = db.relationship("HistoricSite", back_populates="city")

    def __repr__(self):
        return f"<City {self.name}>"
