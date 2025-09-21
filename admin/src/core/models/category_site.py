from core.database import db
from datetime import datetime, timezone

class CategorySite(db.Model):
    __tablename__ = "category_site"
    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(150), nullable = False)
    historic_sites = db.relationship("HistoricSite", back_populates = "category_site")