from core.database import db

role_permission = db.Table(
    "role_permission",
    db.Column("role_id", db.Integer, db.ForeignKey("role.id"), primary_key=True),
    db.Column(
        "permission_id", db.Integer, db.ForeignKey("permission.id"), primary_key=True
    ),
)


class Role(db.Model):
    __tablename__ = "role"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    users = db.relationship("User", back_populates="role", lazy="dynamic")
    permissions = db.relationship(
        "Permission",
        secondary="role_permission",
        back_populates="roles",
    )

    def __repr__(self):
        return f"<Role {self.name}>"

    def has_permission(self, permission_name):
        """Verifica si el rol tiene un permiso específico."""
        return any(
            permission.name == permission_name for permission in self.permissions
        )

    def has_users(self):
        """Verifica si el rol tiene usuarios asignados"""
        return self.users.count() > 0

    def get_users_count(self):
        """Obtiene el número de usuarios con este rol"""
        return self.users.count()
