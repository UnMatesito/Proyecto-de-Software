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

    # Atributos
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    # Relaciones
    users = db.relationship(
        "User", back_populates="role", lazy="dynamic", cascade="all, delete-orphan"
    )
    permissions = db.relationship(
        "Permission",
        secondary="role_permission",
        back_populates="roles",
    )

    # Metodos
    def has_permission(self, permission_name):
        """
        Verifica si el rol tiene un permiso específico.

        Args:
            permission_name (str): Nombre del permiso a verificar.

        Returns:
            bool: True si el rol tiene el permiso, False en caso contrario.
        """
        return any(
            permission.name == permission_name for permission in self.permissions
        )

    def add_permission(self, permission):
        """
        Agrega un permiso al rol si no lo tiene.

        Args:
            permission (Permission): Permiso a agregar.
        """
        if not self.has_permission(permission.name):
            self.permissions.append(permission)
            db.session.commit()

    def remove_permission(self, permission):
        """
        Elimina un permiso del rol si está asignado.

        Args:
            permission (Permission): Permiso a eliminar.
        """
        if self.has_permission(permission.name):
            self.permissions.remove(permission)
            db.session.commit()

    def has_users(self):
        """
        Verifica si hay usuarios asignados al rol.

        Returns:
            bool: True si existen usuarios asociados.
        """
        return self.users.count() > 0

    def can_be_deleted(self):
        """
        Determina si el rol puede ser eliminado.

        Returns:
            bool: True si el rol no tiene usuarios asignados, False en caso contrario.
        """
        return not self.has_users()

    def get_users_count(self):
        """
        Devuelve la cantidad de usuarios asociados a este rol.

        Returns:
            int: Número de usuarios.
        """
        return self.users.count()

    def __repr__(self):
        return f"<Role {self.name}>"
