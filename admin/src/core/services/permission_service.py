from typing import List, Optional, Dict
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from core.database import db
from core.models.permission import Permission
from core.models.role import Role


def get_all_permissions() -> List[Permission]:
    """Obtiene todos los permisos"""
    return Permission.query.all()


def get_permission_by_id(permission_id: int) -> Optional[Permission]:
    """Obtiene un permiso por su ID"""
    return Permission.query.get(permission_id)


def get_permission_by_name(name: str) -> Optional[Permission]:
    """Obtiene un permiso por su nombre"""
    return Permission.query.filter_by(name=name).first()


def create_permission(name: str, description: str) -> Permission:
    """Crea un nuevo permiso"""
    try:
        permission = Permission(name=name, description=description)
        db.session.add(permission)
        db.session.commit()
        return permission
    except IntegrityError:
        db.session.rollback()
        raise ValueError(f"Ya existe un permiso con el nombre '{name}'")


def create_multiple_permissions(permissions_data: List[Dict[str, str]]) -> List[Permission]:
    """
    Crea múltiples permisos

    Args:
        permissions_data: Lista de diccionarios con 'name' y 'description'

    Returns:
        Lista de permisos creados
    """
    created_permissions = []
    errors = []

    for perm_data in permissions_data:
        try:
            name = perm_data.get('name')
            description = perm_data.get('description')

            if not name or not description:
                errors.append(f"Datos incompletos: {perm_data}")
                continue

            permission = Permission(name=name, description=description)
            db.session.add(permission)
            created_permissions.append(permission)

        except Exception as e:
            errors.append(f"Error creando permiso '{perm_data.get('name', 'Unknown')}': {str(e)}")

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        # Intentar identificar qué nombre causó el conflicto
        if 'UNIQUE constraint failed' in str(e) or 'duplicate key' in str(e):
            raise ValueError(f"Uno o más permisos ya existen. Error: {str(e)}")
        raise ValueError(f"Error de integridad al crear permisos: {str(e)}")

    if errors:
        # Si hay errores pero algunos permisos se crearon, informar sobre ambos
        error_msg = "Algunos permisos no pudieron ser creados: " + "; ".join(errors)
        if created_permissions:
            error_msg += f". Se crearon exitosamente {len(created_permissions)} permisos."
        raise ValueError(error_msg)

    return created_permissions


def update_permission(permission_id: int, name: str = None, description: str = None) -> Permission:
    """
    Actualiza el nombre y/o descripción de un permiso

    Args:
        permission_id: ID del permiso a actualizar
        name: Nuevo nombre (opcional)
        description: Nueva descripción (opcional)
    """
    try:
        permission = Permission.query.get(permission_id)
        if not permission:
            raise ValueError(f"No existe un permiso con ID {permission_id}")

        if name is not None:
            permission.name = name
        if description is not None:
            permission.description = description

        if name is None and description is None:
            raise ValueError("Debe proporcionar al menos un campo para actualizar (name o description)")

        db.session.commit()
        return permission
    except IntegrityError:
        db.session.rollback()
        if name:
            raise ValueError(f"Ya existe un permiso con el nombre '{name}'")
        raise ValueError("Error de integridad al actualizar el permiso")


def get_permission_roles(permission_id: int) -> List[Role]:
    """Obtiene los roles que tienen asignado un permiso específico"""
    permission = Permission.query.options(joinedload(Permission.roles)).get(permission_id)
    if not permission:
        raise ValueError(f"No existe un permiso con ID {permission_id}")

    return permission.roles


def permission_exists(permission_id: int) -> bool:
    """Verifica si un permiso existe por ID"""
    return Permission.query.get(permission_id) is not None


def permission_exists_by_name(name: str) -> bool:
    """Verifica si un permiso existe por nombre"""
    return Permission.query.filter_by(name=name).first() is not None


def get_permissions_count() -> int:
    """Obtiene la cantidad total de permisos que existen"""
    return Permission.query.count()


def delete_permission(permission_id: int) -> bool:
    """
    Elimina un permiso. Nota: Esto también eliminará las relaciones con roles

    Returns:
        True si se eliminó exitosamente
    """
    permission = Permission.query.get(permission_id)
    if not permission:
        raise ValueError(f"No existe un permiso con ID {permission_id}")

    # SQLAlchemy manejará automáticamente la eliminación de las relaciones
    # en la tabla intermedia role_permission debido a la configuración de relationships
    db.session.delete(permission)
    db.session.commit()
    return True


def get_permissions_by_role_count() -> Dict[int, int]:
    """
    Obtiene un diccionario con la cantidad de roles que tienen cada permiso

    Returns:
        Dict con permission_id como clave y cantidad de roles como valor
    """
    permissions = Permission.query.options(joinedload(Permission.roles)).all()
    return {permission.id: len(permission.roles) for permission in permissions}


def search_permissions_by_name(search_term: str) -> List[Permission]:
    """Busca permisos que contengan el término de búsqueda en su nombre"""
    return Permission.query.filter(Permission.name.ilike(f'%{search_term}%')).all()


def search_permissions_by_description(search_term: str) -> List[Permission]:
    """Busca permisos que contengan el término de búsqueda en su descripción"""
    return Permission.query.filter(Permission.description.ilike(f'%{search_term}%')).all()