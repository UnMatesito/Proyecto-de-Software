from core.database import db


class City(db.Model):
    __tablename__ = "city"

    # Atributos
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)

    # Relaciones
    province_id = db.Column(
        db.Integer, db.ForeignKey("province.id", ondelete="CASCADE")
    )
    province = db.relationship("Province", back_populates="cities")

    historic_sites = db.relationship(
        "HistoricSite", back_populates="city", cascade="all, delete-orphan"
    )

    # Metodos
    def __repr__(self):
        return f"<City {self.name}>"
