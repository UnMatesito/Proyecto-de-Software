from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError

from core.database import db
from core.models import Role, User


def get_all_users():
    return User.query.all()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


def create_user(**kwargs):
    if User.query.filter_by(email=kwargs.get("email")).first():
        raise ValueError("Ya existe un usuario con ese email")

    raw_password = kwargs.pop("password", None)
    user = User(**kwargs)

    if raw_password:
        user.password = raw_password

    db.session.add(user)

    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error al crear el usuario: {e}")
    return user


def update_user_attribute(user_id, attr_name, new_value, check_func=None):
    """
    Función genérica para actualizar atributos de usuario
    - user_id: ID del usuario a modificar
    - attr_name: nombre del atributo a modificar
    - new_value: nuevo valor para el atributo
    - check_func: función opcional para verificar condiciones antes del update
    """
    # Checkeo si existe el usuario
    user = User.query.get(user_id)
    if not user:
        raise ValueError(f"No existe el usuario con id {user_id}")

    if check_func:
        msg = check_func(user)
        if msg:
            raise ValueError(msg)

    # Verificar que el atributo existe en el modelo
    if hasattr(user, attr_name):
        setattr(user, attr_name, new_value)
    else:
        raise AttributeError(f"{attr_name} no es un atributo de User")
    # Intento actualizar la db
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error al actualizar el usuario: {e}")
    return True


def delete_user(user_id):
    """Marca un usuario como eliminado (soft delete)"""

    def check_delete(user):
        if user.deleted_at is not None:
            return f"El usuario {user.first_name} ya está eliminado"
        return None

    return update_user_attribute(
        user_id, "deleted_at", datetime.now(timezone.utc), check_delete
    )


def block_user(user_id):
    """Bloquea un usuario"""

    def check_blocked(user):
        if user.blocked:
            return f"El usuario {user.first_name} ya está bloqueado"
        return None

    return update_user_attribute(user_id, "blocked", True, check_blocked)


def unblock_user(user_id):
    """Desbloquea un usuario"""

    def check_blocked(user):
        if not user.blocked:
            return f"El usuario {user.first_name} ya está desbloqueado"
        return None

    return update_user_attribute(user_id, "blocked", False, check_blocked)


def change_password(user_id, old_password, new_password):
    """Cambia la contraseña de un usuario"""
    user = User.query.get(user_id)
    if not user:
        raise ValueError(f"No existe el usuario con id {user_id}")

    if not user.check_password(old_password):
        raise ValueError("La contraseña actual no es correcta")

    if user.check_password(new_password):
        raise ValueError("La nueva contraseña no puede ser igual a la anterior")

    user.password = new_password

    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error al actualizar la contraseña: {e}")
    return True


def assign_role(user_id, role_id):
    """Asigna un rol a un usuario"""
    role = Role.query.get(role_id)
    if not role:
        raise ValueError(f"No existe el rol con id {role_id}")

    def role_check(user):
        if user.check_role(role_id):
            return f"El usuario {user.first_name} ya tiene dicho rol"
        return None

    return update_user_attribute(user_id, "role_id", role_id, role_check)
