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
    # role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    created_at = db.Column(db.DateTime, default=lambda: DateTime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: DateTime.now(timezone.utc))
    deleted_at = db.Column(db.DateTime)
    bocked = db.Column(db.Boolean, nullable=False, default=False)
    password_hash = db.Column(db.String(255), nullable=False)
    # role = db.relationship("Role", back_populates="users")

    inserted_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    site_histories = db.relationship("SiteHistory", back_populates="user")
    

    """Funcion propia para setear una contraseña con bcryp, "raw_password: str" NO obliga a que el parametro sea un str, es solo una notacion y ayuda a detectar errores    """
    def set_password(self, new_password: str):
        password_hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()) #Creo el hash de la password
        self.password_hash= password_hashed.decode("utf-8") #La guardo en un string legible 

    def __repr__(self):
        return f"<User {self.first_name}>"