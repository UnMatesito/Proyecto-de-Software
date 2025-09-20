from core.database import db
from datetime import datetime, timezone

class Province(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)