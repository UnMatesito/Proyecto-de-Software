from core.database import db


class Province(db.Model):
    __tablename__ = "province"

    # Atributos
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)

    # Relaciones
    cities = db.relationship(
        "City", back_populates="province", cascade="all, delete-orphan"
    )

    # Metodos
    def __repr__(self):
        return f"<Province {self.name}>"
