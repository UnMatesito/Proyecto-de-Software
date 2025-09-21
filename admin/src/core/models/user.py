from datetime import datetime, timezone

from core.database import db
from core.utils.bcrypt import bcrypt


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    first_name = db.Column(db.String(50), nullable=False, unique=True)
    last_name = db.Column(db.String(50), nullable=False, unique=True)
    active = db.Column(db.Boolean, default=True)
    system_admin = db.Column(db.Boolean, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    deleted_at = db.Column(db.DateTime)
    bocked = db.Column(db.Boolean, nullable=False, default=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.relationship("Role", back_populates="users")
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    site_histories = db.relationship("SiteHistory", back_populates="user")

    historic_sites = db.relationship(
        "HistoricSite", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def password(self):
        raise AttributeError("La contraseña no es un atributo legible")

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.first_name}>"
