from core.database import db 
from datetime import datetime, timezone

class City(db.Model):
    __tablename__ = "city"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150), nullable = False)