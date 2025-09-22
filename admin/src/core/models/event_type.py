from core.database import db


class EventType(db.Model):
    __tablename__ = "event_type"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    site_histories = db.relationship("SiteHistory", back_populates="event_type")

    def __repr__(self):
        return f"<EventType {self.name}>"
