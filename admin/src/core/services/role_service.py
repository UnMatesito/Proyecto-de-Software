from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from core.database import db
from core.models.permission import Permission
from core.models.role import Role

"""
Módulo de servicios para la gestión de roles del sistema.
Incluye operaciones CRUD y asignación o eliminación de permisos asociados a roles.
"""


def get_all_roles() -> List[Role]:
    """
    Obtiene todos los roles registrados en el sistema.

    Returns:
        List[Role]: Lista de todas las instancias de roles existentes.
    """
    return Role.query.all()


def get_role_by_id(role_id: int) -> Optional[Role]:
    """
    Obtiene un rol específico por su ID.

    Args:
        role_id (int): ID del rol a buscar.

    Returns:
        Optional[Role]: Rol encontrado o None si no existe.
    """
    return Role.query.get(role_id)


def get_role_by_name(name: str) -> Optional[Role]:
    """
    Obtiene un rol específico por su nombre.

    Args:
        name (str): Nombre del rol a buscar.

    Returns:
        Optional[Role]: Rol encontrado o None si no existe.
    """
    return Role.query.filter_by(name=name).first()


def create_role_without_permissions(name: str) -> Role:
    """
    Crea un nuevo rol sin permisos asignados.

    Args:
        name (str): Nombre del nuevo rol.

    Returns:
        Role: Instancia del rol creado.

    Raises:
        ValueError: Si ya existe un rol con el mismo nombre.
    """
    try:
        role = Role(name=name)
        db.session.add(role)
        db.session.commit()
        return role
    except IntegrityError:
        db.session.rollback()
        raise ValueError(f"Ya existe un rol con el nombre '{name}'")


def create_role_with_permissions(name: str, permission_ids: List[int]) -> Role:
    """
    Crea un nuevo rol con una lista de permisos asignados.

    Args:
        name (str): Nombre del nuevo rol.
        permission_ids (List[int]): Lista de IDs de permisos a asignar.

    Returns:
        Role: Instancia del rol creado.

    Raises:
        ValueError: Si uno o más permisos no existen o si el nombre del rol ya está en uso.
    """
    try:
        # Verificar que todos los permisos existan
        permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()
        if len(permissions) != len(permission_ids):
            found_ids = [p.id for p in permissions]
            missing_ids = [pid for pid in permission_ids if pid not in found_ids]
            raise ValueError(f"Los siguientes permisos no existen: {missing_ids}")

        role = Role(name=name)
        role.permissions = permissions
        db.session.add(role)
        db.session.commit()
        return role
    except IntegrityError:
        db.session.rollback()
        raise ValueError(f"Ya existe un rol con el nombre '{name}'")


def assign_permission_to_role(role_id: int, permission_id: int) -> bool:
    """
    Asigna un permiso a un rol existente.

    Args:
        role_id (int): ID del rol.
        permission_id (int): ID del permiso.

    Returns:
        bool: True si se asignó correctamente, False si ya lo tenía.

    Raises:
        ValueError: Si el rol o el permiso no existen.
    """
    role = Role.query.get(role_id)
    if not role:
        raise ValueError(f"No existe un rol con ID {role_id}")

    permission = Permission.query.get(permission_id)
    if not permission:
        raise ValueError(f"No existe un permiso con ID {permission_id}")

    if permission in role.permissions:
        return False  # El permiso ya está asignado

    role.permissions.append(permission)
    db.session.commit()
    return True


def assign_multiple_permissions_to_role(
    role_id: int, permission_ids: List[int]
) -> dict:
    """
    Asigna múltiples permisos a un rol existente.

    Args:
        role_id (int): ID del rol.
        permission_ids (List[int]): Lista de IDs de permisos a asignar.

    Returns:
        dict: Diccionario con resultados de la asignación.

    Raises:
        ValueError: Si alguno de los permisos no existe.
    """
    role = Role.query.get(role_id)
    if not role:
        raise ValueError(f"No existe un rol con ID {role_id}")

    # Verificar que todos los permisos existan
    permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()
    if len(permissions) != len(permission_ids):
        found_ids = [p.id for p in permissions]
        missing_ids = [pid for pid in permission_ids if pid not in found_ids]
        raise ValueError(f"Los siguientes permisos no existen: {missing_ids}")

    # Separar permisos ya asignados de los nuevos
    current_permission_ids = [p.id for p in role.permissions]
    new_permissions = [p for p in permissions if p.id not in current_permission_ids]
    already_assigned = [p.id for p in permissions if p.id in current_permission_ids]

    # Asignar nuevos permisos
    for permission in new_permissions:
        role.permissions.append(permission)

    db.session.commit()

    return {
        "assigned": [p.id for p in new_permissions],
        "already_assigned": already_assigned,
        "total_assigned": len(new_permissions),
    }


def remove_permission_from_role(role_id: int, permission_id: int) -> bool:
    """
    Elimina un permiso de un rol existente.

    Args:
        role_id (int): ID del rol.
        permission_id (int): ID del permiso.

    Returns:
        bool: True si se eliminó correctamente, False si el permiso no estaba asignado.

    Raises:
        ValueError: Si el rol o el permiso no existen.
    """
    role = Role.query.get(role_id)
    if not role:
        raise ValueError(f"No existe un rol con ID {role_id}")

    permission = Permission.query.get(permission_id)
    if not permission:
        raise ValueError(f"No existe un permiso con ID {permission_id}")

    if permission not in role.permissions:
        return False  # El permiso no estaba asignado

    role.permissions.remove(permission)
    db.session.commit()
    return True


def remove_multiple_permissions_from_role(
    role_id: int, permission_ids: List[int]
) -> dict:
    """
    Elimina varios permisos de un rol.

    Args:
        role_id (int): ID del rol.
        permission_ids (List[int]): IDs de permisos a eliminar.

    Returns:
        dict: Resultado con los permisos eliminados y no asignados.
    """
    role = Role.query.get(role_id)
    if not role:
        raise ValueError(f"No existe un rol con ID {role_id}")

    # Verificar que todos los permisos existan
    permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()
    if len(permissions) != len(permission_ids):
        found_ids = [p.id for p in permissions]
        missing_ids = [pid for pid in permission_ids if pid not in found_ids]
        raise ValueError(f"Los siguientes permisos no existen: {missing_ids}")

    # Separar permisos asignados de los no asignados
    current_permissions = {p.id: p for p in role.permissions}
    removed_permissions = []
    not_assigned = []

    for permission in permissions:
        if permission.id in current_permissions:
            role.permissions.remove(permission)
            removed_permissions.append(permission.id)
        else:
            not_assigned.append(permission.id)

    db.session.commit()

    return {
        "removed": removed_permissions,
        "not_assigned": not_assigned,
        "total_removed": len(removed_permissions),
    }


def delete_role(role_id: int) -> bool:
    """
    Elimina un rol del sistema, siempre que no tenga usuarios asignados.

    Args:
        role_id (int): ID del rol a eliminar.

    Returns:
        bool: True si se eliminó correctamente.

    Raises:
        ValueError: Si el rol no existe o tiene usuarios asignados.
    """
    role = Role.query.get(role_id)
    if not role:
        raise ValueError(f"No existe un rol con ID {role_id}")

    if role.has_users():
        raise ValueError(
            f"No se puede eliminar el rol '{role.name}' porque tiene {role.get_users_count()} usuarios asignados"
        )

    db.session.delete(role)
    db.session.commit()
    return True


def role_has_permission(role_id: int, permission_name: str) -> bool:
    """
    Verifica si un rol tiene asignado un permiso específico.

    Args:
        role_id (int): ID del rol.
        permission_name (str): Nombre del permiso a verificar.

    Returns:
        bool: True si el rol tiene el permiso, False en caso contrario.
    """
    role = Role.query.get(role_id)
    if not role:
        raise ValueError(f"No existe un rol con ID {role_id}")

    return role.has_permission(permission_name)


def get_role_permissions(role_id: int) -> List[Permission]:
    """
    Obtiene todos los permisos asociados a un rol.

    Args:
        role_id (int): ID del rol.

    Returns:
        List[Permission]: Lista de permisos del rol.

    Raises:
        ValueError: Si el rol no existe.
    """
    role = Role.query.options(joinedload(Role.permissions)).get(role_id)
    if not role:
        raise ValueError(f"No existe un rol con ID {role_id}")

    return role.permissions


def clear_role_permissions(role_id: int) -> int:
    """
    Elimina todos los permisos asociados a un rol.

    Args:
        role_id (int): ID del rol cuyos permisos se eliminarán.

    Returns:
        int: Cantidad de permisos eliminados.

    Raises:
        ValueError: Si el rol no existe en la base de datos.
    """
    role = Role.query.options(joinedload(Role.permissions)).get(role_id)
    if not role:
        raise ValueError(f"No existe un rol con ID {role_id}")

    permissions_count = len(role.permissions)
    role.permissions.clear()
    db.session.commit()
    return permissions_count


def role_exists(role_id: int) -> bool:
    """
    Verifica si un rol existe en la base de datos según su ID.

    Args:
        role_id (int): ID del rol a verificar.

    Returns:
        bool: True si el rol existe, False en caso contrario.
    """
    return Role.query.get(role_id) is not None


def role_exists_by_name(name: str) -> bool:
    """
    Verifica si un rol existe en la base de datos según su nombre.

    Args:
        name (str): Nombre del rol a verificar.

    Returns:
        bool: True si el rol existe, False en caso contrario.
    """
    return Role.query.filter_by(name=name).first() is not None


def can_delete_role(role_id: int) -> bool:
    """
    Determina si un rol puede ser eliminado, es decir, si no tiene usuarios asignados.

    Args:
        role_id (int): ID del rol a verificar.

    Returns:
        bool: True si el rol no tiene usuarios asociados, False en caso contrario o en caso de que no exista el rol.
    """
    role = Role.query.get(role_id)
    if not role:
        return False  # No existe el rol

    return not role.has_users()


def get_roles_count() -> int:
    """
    Obtiene la cantidad total de roles existentes.

    Returns:
        int: Número de roles registrados en el sistema.
    """
    return Role.query.count()


def get_role_users_count(role_id: int) -> int:
    """
    Obtiene la cantidad de usuarios asociados a un rol específico.

    Args:
        role_id (int): ID del rol.

    Returns:
        int: Número de usuarios asignados a ese rol.

    Raises:
        ValueError: Si el rol no existe.
    """
    role = Role.query.get(role_id)
    if not role:
        raise ValueError(f"No existe un rol con ID {role_id}")

    return role.get_users_count()


def update_role_name(role_id: int, new_name: str) -> Role:
    """
    Actualiza el nombre de un rol existente.

    Args:
        role_id (int): ID del rol.
        new_name (str): Nuevo nombre del rol.

    Returns:
        Role: Rol actualizado.

    Raises:
        ValueError: Si el nombre ya existe o el rol no fue encontrado.
    """
    try:
        role = Role.query.get(role_id)
        if not role:
            raise ValueError(f"No existe un rol con ID {role_id}")

        role.name = new_name
        db.session.commit()
        return role
    except IntegrityError:
        db.session.rollback()
        raise ValueError(f"Ya existe un rol con el nombre '{new_name}'")
