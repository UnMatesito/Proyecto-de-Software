from typing import Dict, List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from core.database import db
from core.models.permission import Permission
from core.models.role import Role

"""
Módulo de servicios para la gestión de permisos.
Incluye operaciones CRUD, búsquedas y vinculación con roles.
"""


def get_all_permissions() -> List[Permission]:
    """
    Obtiene todos los permisos del sistema.

    Returns:
        List[Permission]: Lista de permisos existentes.
    """
    return Permission.query.all()


def get_permission_by_id(permission_id: int) -> Optional[Permission]:
    """
    Obtiene un permiso por su ID.

    Args:
        permission_id (int): ID del permiso.

    Returns:
        Optional[Permission]: Permiso encontrado o None.
    """
    return Permission.query.get(permission_id)


def get_permission_by_name(name: str) -> Optional[Permission]:
    """
    Obtiene un permiso por su nombre.

    Args:
        name (str): Nombre del permiso.

    Returns:
        Optional[Permission]: Permiso encontrado o None.
    """
    return Permission.query.filter_by(name=name).first()


def create_permission(name: str, description: str) -> Permission:
    """
    Crea un nuevo permiso.

    Args:
        name (str): Nombre del permiso.
        description (str): Descripción del permiso.

    Returns:
        Permission: Instancia del permiso creado.

    Raises:
        ValueError: Si el nombre ya existe.
    """
    try:
        permission = Permission(name=name, description=description)
        db.session.add(permission)
        db.session.commit()
        return permission
    except IntegrityError:
        db.session.rollback()
        raise ValueError(f"Ya existe un permiso con el nombre '{name}'")


def create_multiple_permissions(
    permissions_data: List[Dict[str, str]],
) -> List[Permission]:
    """
    Crea múltiples permisos a la vez.

    Args:
        permissions_data (List[Dict[str, str]]): Lista con nombre y descripción.

    Returns:
        List[Permission]: Lista de permisos creados.

    Raises:
        ValueError: Si existen duplicados o datos incompletos.
    """
    created_permissions = []
    errors = []

    for perm_data in permissions_data:
        try:
            name = perm_data.get("name")
            description = perm_data.get("description")

            if not name or not description:
                errors.append(f"Datos incompletos: {perm_data}")
                continue

            permission = Permission(name=name, description=description)
            db.session.add(permission)
            created_permissions.append(permission)

        except Exception as e:
            errors.append(
                f"Error creando permiso '{perm_data.get('name', 'Unknown')}': {str(e)}"
            )

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        # Intentar identificar qué nombre causó el conflicto
        if "UNIQUE constraint failed" in str(e) or "duplicate key" in str(e):
            raise ValueError(f"Uno o más permisos ya existen. Error: {str(e)}")
        raise ValueError(f"Error de integridad al crear permisos: {str(e)}")

    if errors:
        # Si hay errores pero algunos permisos se crearon, informar sobre ambos
        error_msg = "Algunos permisos no pudieron ser creados: " + "; ".join(errors)
        if created_permissions:
            error_msg += (
                f". Se crearon exitosamente {len(created_permissions)} permisos."
            )
        raise ValueError(error_msg)

    return created_permissions


def update_permission(
    permission_id: int, name: str = None, description: str = None
) -> Permission:
    """
    Actualiza los datos de un permiso existente.

    Args:
        permission_id (int): ID del permiso.
        name (str, optional): Nuevo nombre.
        description (str, optional): Nueva descripción.

    Returns:
        Permission: Permiso actualizado.

    Raises:
        ValueError: Si el permiso no existe o el nombre ya está en uso.
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
            raise ValueError(
                "Debe proporcionar al menos un campo para actualizar (name o description)"
            )

        db.session.commit()
        return permission
    except IntegrityError:
        db.session.rollback()
        if name:
            raise ValueError(f"Ya existe un permiso con el nombre '{name}'")
        raise ValueError("Error de integridad al actualizar el permiso")


def get_permission_roles(permission_id: int) -> List[Role]:
    """
    Obtiene los roles que poseen un permiso específico.

    Args:
        permission_id (int): ID del permiso.

    Returns:
        List[Role]: Lista de roles asociados.
    """
    permission = Permission.query.options(joinedload(Permission.roles)).get(
        permission_id
    )
    if not permission:
        raise ValueError(f"No existe un permiso con ID {permission_id}")

    return permission.roles


def permission_exists(permission_id: int) -> bool:
    """
    Verifica si un permiso existe en la base de datos según su ID.

    Args:
        permission_id (int): ID del permiso a verificar.

    Returns:
        bool: True si el permiso existe, False en caso contrario.
    """
    return Permission.query.get(permission_id) is not None


def permission_exists_by_name(name: str) -> bool:
    """
    Verifica si un permiso existe en la base de datos según su nombre.

    Args:
        name (str): Nombre del permiso a verificar.

    Returns:
        bool: True si el permiso existe, False en caso contrario.
    """
    return Permission.query.filter_by(name=name).first() is not None


def get_permissions_count() -> int:
    """
    Obtiene la cantidad total de permisos registrados en el sistema.

    Returns:
        int: Número total de permisos existentes.
    """
    return Permission.query.count()


def delete_permission(permission_id: int) -> bool:
    """
    Elimina un permiso del sistema.

    Args:
        permission_id (int): ID del permiso.

    Returns:
        bool: True si se eliminó correctamente.

    Raises:
        ValueError: Si el permiso no existe.
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
    """
    Busca permisos por nombre.

    Args:
        search_term (str): Texto de búsqueda.

    Returns:
        List[Permission]: Permisos cuyo nombre contiene el término.
    """
    return Permission.query.filter(Permission.name.ilike(f"%{search_term}%")).all()


def search_permissions_by_description(search_term: str) -> List[Permission]:
    """
    Busca permisos cuyo texto de descripción contenga el término especificado.

    Args:
        search_term (str): Texto o palabra clave a buscar dentro de la descripción de los permisos.

    Returns:
        List[Permission]: Lista de permisos cuya descripción coincide parcialmente con el término de búsqueda.
    """
    return Permission.query.filter(
        Permission.description.ilike(f"%{search_term}%")
    ).all()
