from datetime import datetime, timezone

from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError

from core.database import db
from core.models import Role, User
from core.utils import pagination


def get_all_users():
    """Obtiene todos los usuarios."""
    return User.query.all()


def get_user_by_id(user_id):
    """Obtiene un usuario por su id."""
    return User.query.get(user_id)


def get_user_by_email(email):
    """Obtiene un usuario por su email."""
    return User.query.filter_by(email=email).first()


def get_paginated_users(
    page=1,
    order_by="created_at",
    sorted_by="asc",
    blocked=None,
    role_id=None,
    email=None,
):
    """Paginacion de usuarios ordenado por creacion
    -sorted_by ordenado asc o des
    -order_by en usuario es solo por fecha de creacion
    -active parametro para filtrar por activo
    -role_id parametro para filtrar por rol
    """
    query = User.query
    if blocked == "1":
        query = query.filter_by(blocked=True)
    elif blocked == "0":
        query = query.filter_by(blocked=False)
    if role_id:
        query = query.filter_by(role_id=int(role_id))
    if email:
        query = query.filter_by(email=email)
    if order_by == "created_at":
        if sorted_by == "asc":
            query = query.order_by(User.created_at)
        else:
            query = query.order_by(desc(User.created_at))
    return pagination.paginate_query(
        query, page=page, order_by=order_by, sorted_by=sorted_by
    )


def create_user(**kwargs):
    """Crea un nuevo usuario."""
    if User.query.filter_by(
        email=kwargs.get("email")
    ).first():  # Valido que el mail no exista
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


def update_user_with_action(user_id, action_func):
    """
    Función genérica para ejecutar acciones sobre un usuario
    - user_id: ID del usuario a modificar
    - action_func: función que recibe el usuario y ejecuta la acción
    """
    # Checkeo si existe el usuario
    user = User.query.get(user_id)
    if not user:
        raise ValueError(f"No existe el usuario con id {user_id}")

    # Ejecutar la función de acción
    msg = action_func(user)
    if msg:
        raise ValueError(msg)

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
        # Si es system admin
        if user.is_admin():
            return f"El usuario {user.first_name} es Administrador del sistema y no puede ser eliminado"
        return None

    return update_user_attribute(
        user_id, "deleted_at", datetime.now(timezone.utc), check_delete
    )


def restore_user(user_id):
    """Desmarca un usuario como eliminado"""

    def check_delete(user):
        if user.deleted_at is None:
            return f"El usuario {user.first_name} no esta eliminado"
        return None

    return update_user_attribute(user_id, "deleted_at", None, check_delete)


def block_user(user_id):
    """Bloquea un usuario"""

    def check_and_block(user):
        if user.blocked:
            return f"El usuario {user.first_name} ya está bloqueado"
        try:
            user.block_user()
            return None
        except ValueError as e:
            return str(e)

    return update_user_with_action(user_id, check_and_block)


def unblock_user(user_id):
    """Desbloquea un usuario"""

    def check_and_unblock(user):
        if not user.blocked:
            return f"El usuario {user.first_name} ya está desbloqueado"

        user.unblock_user()
        return None

    return update_user_with_action(user_id, check_and_unblock)


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


def change_password_by_admin(user_id, new_password):
    """Admin cambia la contraseña de un usuario"""
    user = User.query.get(user_id)
    if not user:
        raise ValueError("No existe tal usaurio")
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
    """Asigna un rol a un usuario y desactiva system_admin si corresponde"""
    role = Role.query.get(role_id)
    if not role:
        raise ValueError(f"No existe el rol con id {role_id}")

    user = User.query.get(user_id)
    if not user:
        raise ValueError(f"No existe el usuario con id {user_id}")

    # Verificar si ya tiene ese rol
    if user.check_role(role_id):
        raise ValueError(
            f"El usuario {user.get_full_name()} ya tiene el rol '{role.name}'"
        )

    # Asignar nuevo rol
    user.role_id = role_id

    # Si tenía system_admin, desactivarlo
    if user.is_admin():
        user.system_admin = False

    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error al asignar el rol: {e}")

    return True


def toggle_system_admin(user_id, make_admin: bool):
    """
    Convierte un usuario en System Admin o le quita ese rol.
    Si se convierte en System Admin, también se asegura que el rol sea Administrador.
    """
    user = User.query.get(user_id)
    if not user:
        raise ValueError(f"No existe el usuario con id {user_id}")

    # Evitar cambios redundantes
    if user.system_admin == make_admin:
        estado = "ya es" if make_admin else "ya no es"
        raise ValueError(f"El usuario {user.first_name} {estado} System Admin")

    user.system_admin = make_admin

    if make_admin:
        # Buscar rol Administrador
        admin_role = Role.query.filter_by(name="Administrador").first()
        if not admin_role:
            raise RuntimeError("No se encontró el rol 'Administrador'")
        user.role_id = admin_role.id

    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error al actualizar el usuario: {e}")

    return True

def get_user_history():
    """Obtiene todos los usuarios systemAdmin/admin/editores"""
    return User.query.filter(
        (User.role.has(name="Administrador")) |
        (User.role.has(name="Editor")) |
        (User.system_admin == True)
    ).all()
