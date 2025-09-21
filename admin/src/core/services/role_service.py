from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from core.database import db
from core.models.role import Role
from core.models.permission import Permission


def get_all_roles() -> List[Role]:
    """Obtiene todos los roles"""
    return Role.query.all()


def get_role_by_id(role_id: int) -> Optional[Role]:
    """Obtiene un rol por su ID"""
    return Role.query.get(role_id)


def get_role_by_name(name: str) -> Optional[Role]:
    """Obtiene un rol por su nombre"""
    return Role.query.filter_by(name=name).first()


def create_role_without_permissions(name: str) -> Role:
    """Crea un rol sin permisos"""
    try:
        role = Role(name=name)
        db.session.add(role)
        db.session.commit()
        return role
    except IntegrityError:
        db.session.rollback()
        raise ValueError(f"Ya existe un rol con el nombre '{name}'")


def create_role_with_permissions(name: str, permission_ids: List[int]) -> Role:
    """Crea un rol con permisos específicos"""
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
    """Asigna un permiso a un rol. Retorna True si se asignó, False si ya estaba asignado"""
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


def assign_multiple_permissions_to_role(role_id: int, permission_ids: List[int]) -> dict:
    """Asigna múltiples permisos a un rol. Retorna un dict con resultados"""
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
        'assigned': [p.id for p in new_permissions],
        'already_assigned': already_assigned,
        'total_assigned': len(new_permissions)
    }


def remove_permission_from_role(role_id: int, permission_id: int) -> bool:
    """Elimina un permiso de un rol. Retorna True si se eliminó, False si no estaba asignado"""
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


def remove_multiple_permissions_from_role(role_id: int, permission_ids: List[int]) -> dict:
    """Elimina múltiples permisos de un rol. Retorna un dict con resultados"""
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
        'removed': removed_permissions,
        'not_assigned': not_assigned,
        'total_removed': len(removed_permissions)
    }


def delete_role(role_id: int) -> bool:
    """Elimina un rol si no tiene usuarios asignados"""
    role = Role.query.get(role_id)
    if not role:
        raise ValueError(f"No existe un rol con ID {role_id}")

    if role.has_users():
        raise ValueError(f"No se puede eliminar el rol '{role.name}' porque tiene {role.get_users_count()} usuarios asignados")

    db.session.delete(role)
    db.session.commit()
    return True


def role_has_permission(role_id: int, permission_name: str) -> bool:
    """Verifica si un rol tiene un permiso específico"""
    role = Role.query.get(role_id)
    if not role:
        raise ValueError(f"No existe un rol con ID {role_id}")

    return role.has_permission(permission_name)


def get_role_permissions(role_id: int) -> List[Permission]:
    """Obtiene todos los permisos de un rol"""
    role = Role.query.options(joinedload(Role.permissions)).get(role_id)
    if not role:
        raise ValueError(f"No existe un rol con ID {role_id}")

    return role.permissions


def clear_role_permissions(role_id: int) -> int:
    """Elimina todos los permisos de un rol. Retorna la cantidad de permisos eliminados"""
    role = Role.query.options(joinedload(Role.permissions)).get(role_id)
    if not role:
        raise ValueError(f"No existe un rol con ID {role_id}")

    permissions_count = len(role.permissions)
    role.permissions.clear()
    db.session.commit()
    return permissions_count


def role_exists(role_id: int) -> bool:
    """Verifica si un rol existe por ID"""
    return Role.query.get(role_id) is not None


def role_exists_by_name(name: str) -> bool:
    """Verifica si un rol existe por nombre"""
    return Role.query.filter_by(name=name).first() is not None


def can_delete_role(role_id: int) -> bool:
    """Verifica si un rol puede ser eliminado (no tiene usuarios asignados)"""
    role = Role.query.get(role_id)
    if not role:
        return False  # No existe el rol

    return not role.has_users()


def get_roles_count() -> int:
    """Obtiene la cantidad total de roles"""
    return Role.query.count()


def get_role_users_count(role_id: int) -> int:
    """Obtiene la cantidad de usuarios que tienen un rol específico"""
    role = Role.query.get(role_id)
    if not role:
        raise ValueError(f"No existe un rol con ID {role_id}")

    return role.get_users_count()


def update_role_name(role_id: int, new_name: str) -> Role:
    """Actualiza el nombre de un rol"""
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