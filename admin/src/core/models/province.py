from datetime import datetime, timezone

from core.database import db


class Province(db.Model):
    __tablename__ = "province"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    cities = db.relationship("City", back_populates="province")

    def __repr__(self):
        return f"<Province {self.name}>"
