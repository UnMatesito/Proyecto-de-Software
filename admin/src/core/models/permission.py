from sqlalchemy.orm import relationship

from core.database import db


class Permission(db.Model):
    __tablename__ = "permission"

    # Atributos
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=False)

    # Relaciones
    roles = relationship(
        "Role",
        secondary="role_permission",
        back_populates="permissions",
    )

    # Metodos
    def __repr__(self):
        return f"<Permission {self.name}>"
