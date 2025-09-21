from datetime import datetime, timezone

import bcrypt

from core.database import db


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    first_name = db.Column(db.String(50), nullable=False, unique=True)
    last_name = db.Column(db.String(50), nullable=False, unique=True)
    active = db.Column(db.Boolean, default=True)
    system_admin = db.Column(db.Boolean, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    deleted_at = db.Column(db.DateTime)
    blocked = db.Column(db.Boolean, nullable=False, default=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.relationship("Role", back_populates="users")
    historic_sites = db.relationship("HistoricSite", back_populates="user")
    inserted_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    """Funcion propia para setear una contraseña con bcryp, "new_password: str" NO obliga a que el parametro sea un str, es solo una notacion y ayuda a detectar errores    """
    def set_password(self, new_password: str):
        password_hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()) #Creo el hash de la password
        self.password_hash= password_hashed.decode("utf-8") #La guardo en un string legible 
    """Funcion propia para checkear la contraseña con bcryp, "new_password: str" NO obliga a que el parametro sea un str, es solo una notacion y ayuda a detectar errores    """
    def check_password(self, passwdord: str):
        return bcrypt.checkpw(passwdord.encode("utf-8"), self.password_hash.encode("utf-8")) #Compara las passwords
    """Funcion para comprobar el rol """
    def check_role(self, new_role_id):
        return self.role_id == new_role_id 

    def __repr__(self):
        return f"<User {self.first_name}>"
