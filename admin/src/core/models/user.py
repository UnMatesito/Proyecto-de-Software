from datetime import datetime, timezone

from core.database import db


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    first_name = db.Column(db.String(50), nullable=False, unique=True)
    last_name = db.Column(db.String(50), nullable=False, unique=True)
    active = db.Column(db.Boolean, nullable=False)
    system_admin = db.Column(db.Boolean, nullable=False)
    # role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    created_at = db.Column(db.DateTime, default=lambda: DateTime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: DateTime.now(timezone.utc))
    deleted_at = db.Column(db.DateTime)
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

    def __repr__(self):
        return f"<User {self.name}>"
