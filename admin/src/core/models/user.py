from datetime import datetime, timezone

from sqlalchemy.orm import validates

from core.database import db
from core.utils.bcrypt import bcrypt


class User(db.Model):
    __tablename__ = "user"

    # Atributos
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    active = db.Column(db.Boolean, default=True)
    system_admin = db.Column(db.Boolean, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False)
    blocked = db.Column(db.Boolean, nullable=False, default=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    deleted_at = db.Column(db.DateTime)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relaciones
    site_histories = db.relationship("SiteHistory", back_populates="user")
    historic_sites = db.relationship(
        "HistoricSite", back_populates="user", cascade="all, delete-orphan"
    )
    role = db.relationship("Role", back_populates="users")

    # Setters y Getters
    @property
    def password(self):
        raise AttributeError("La contraseña no es un atributo legible")

    @password.setter
    def password(self, password: str):
        """
        Funcion para setear una contraseña con bcrypt
        "new_password: str" NO obliga a que el parametro sea un str, es solo una notacion y ayuda a detectar errores
        """
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    # Metodos

    def check_password(self, password):
        """Función para comprobar si la contraseña pasada por parámetro es igual a la asignada al usuario"""
        return bcrypt.check_password_hash(self.password_hash, password)

    def check_role(self, role_id):
        """Funcion para comprobar si tiene un rol en particular por id"""
        return self.role_id == role_id

    def is_admin(self):
        """Funcion para comprobar si el usuario es admin del sistema"""
        return self.system_admin

    def is_active(self):
        return self.blocked is False

    def block_user(self):
        """Bloquea al usuario, excepto si es administrador."""
        if self.is_admin() or self.has_role("Administrador"):
            raise ValueError("No se puede bloquear un administrador")
        self.blocked = True

    def unblock_user(self):
        """Desbloquea al usuario."""
        self.blocked = False

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def delete_user(self):
        self.deleted_at = datetime.now(timezone.utc)
        self.active = False

    def restore_user(self):
        self.deleted_at = None
        self.active = True

    def __repr__(self):
        return f"<User {self.email}>"

    def has_role(self, role_name: str):
        """Funcion para comprobrar si el usuario tiene un rol en particular por nombre"""
        return self.role and self.role.name == role_name

    def has_permission(self, permission_name: str):
        """Comprueba si el rol del usuario tiene dicho permiso"""
        if (
            not self.role or not self.role.permissions
        ):  # Si no tiene rol o si tiene pero no tiene permisos
            return False
        return any(
            p.name == permission_name for p in self.role.permissions
        )  # Recorro los permisos del rol
