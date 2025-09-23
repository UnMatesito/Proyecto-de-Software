from core.database import db


class EventType(db.Model):
    __tablename__ = "event_type"

    # Atributos
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    # Relaciones
    site_histories = db.relationship("SiteHistory", back_populates="event_type")

    # Metodos
    def __repr__(self):
        return f"<EventType {self.name}>"
