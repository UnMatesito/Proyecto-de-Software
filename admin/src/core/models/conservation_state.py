from core.database import db


class ConservationState(db.Model):
    __tablename__ = "conservation_state"

    # Atributos
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(50), nullable=False, unique=True)

    # Relaciones
    historic_sites = db.relationship(
        "HistoricSite", back_populates="conservation_state"
    )

    # Metodos
    def __repr__(self):
        return f"<Conservation state {self.state}>"
