from core.database import db


def run():
    """Ejecuta todos los seeds en orden"""
    print("Iniciando seeders...")

    seed_permissions()
    seed_roles()
    seed_event_types()
    seed_system_admin()
    seed_feature_flags()

    print("Seed finalizado")


def seed_permissions():
    """Crea los permisos básicos del sistema siguiendo el patrón modulo_accion"""
    from core.services import permission_service as PermissionService

    print("Creando permisos...")

    # Permisos para módulo de usuarios (solo Administradores)
    user_permissions = [
        "user_index",  # listar usuarios
        "user_new",  # crear usuario
        "user_update",  # actualizar usuario
        "user_destroy",  # eliminar usuario
        "user_show",  # ver detalle de usuario
        "user_block",  # bloquear/desbloquear usuario
        "user_assign_role",  # asignar roles
    ]

    # Permisos para sitios históricos
    site_permissions = [
        "site_index",  # listar sitios
        "site_new",  # crear sitio
        "site_update",  # actualizar sitio
        "site_destroy",  # eliminar sitio (solo Administradores)
        "site_show",  # ver detalle de sitio
        "site_export",  # exportar sitios (solo Administradores)
        "site_history",  # ver historial de sitio
    ]

    # Permisos para tags
    tag_permissions = [
        "tag_index",  # listar tags
        "tag_new",  # crear tag
        "tag_update",  # actualizar tag
        "tag_destroy",  # eliminar tag
        "tag_show",  # ver detalle de tag
    ]

    # Permisos para feature flags (solo System Admin)
    flag_permissions = [
        "flag_index",  # listar feature flags
        "flag_update",  # actualizar feature flags
    ]

    # Permisos para validación de propuestas (Etapa 2)
    proposal_permissions = [
        "proposal_index",  # listar propuestas
        "proposal_show",  # ver propuesta
        "proposal_approve",  # aprobar propuesta
        "proposal_reject",  # rechazar propuesta
    ]

    # Permisos para moderación de reseñas (Etapa 2)
    review_permissions = [
        "review_index",  # listar reseñas
        "review_show",  # ver reseña
        "review_approve",  # aprobar reseña
        "review_reject",  # rechazar reseña
    ]

    all_permissions = (
        user_permissions
        + site_permissions
        + tag_permissions
        + flag_permissions
        + proposal_permissions
        + review_permissions
    )

    PermissionService.create_permissions_bulk(all_permissions)


def seed_roles():
    """Crea los roles del sistema según los requerimientos del TI"""
    from core.models import Permission
    from core.services import role_service as RoleService

    print("Creando roles...")

    # Obtener todos los permisos
    all_permissions = Permission.query.all()

    # ROL EDITOR
    editor_permission_names = [
        "site_index",
        "site_new",
        "site_update",
        "site_show",
        "site_history",
        "tag_index",
        "tag_new",
        "tag_update",
        "tag_destroy",
        "tag_show",
        "proposal_index",
        "proposal_show",
        "proposal_approve",
        "proposal_reject",
        "review_index",
        "review_show",
        "review_approve",
        "review_reject",
    ]

    editor_permissions = [
        p.id for p in all_permissions if p.name in editor_permission_names
    ]

    RoleService.create_role("Editor", editor_permissions)

    # ROL ADMINISTRADOR
    admin_permission_names = [
        # Usuarios (todos los permisos)
        "user_index",
        "user_new",
        "user_update",
        "user_destroy",
        "user_show",
        "user_block",
        "user_assign_role",
        # Sitios (todos los permisos incluyendo eliminar y exportar)
        "site_index",
        "site_new",
        "site_update",
        "site_destroy",
        "site_show",
        "site_export",
        "site_history",
        # Tags
        "tag_index",
        "tag_new",
        "tag_update",
        "tag_destroy",
        "tag_show",
        # Propuestas y reseñas
        "proposal_index",
        "proposal_show",
        "proposal_approve",
        "proposal_reject",
        "review_index",
        "review_show",
        "review_approve",
        "review_reject",
    ]

    admin_permissions = [
        p.id for p in all_permissions if p.name in admin_permission_names
    ]

    RoleService.create_role("Administrador", admin_permissions)

    # ROL USUARIO PÚBLICO
    RoleService.create_role("Usuario público", [])  # Sin permisos


def seed_event_types():
    """Crea los tipos de eventos para el historial de sitios"""
    from core.models import EventType

    print("Creando tipos de eventos...")

    event_types = [
        # Para sitios históricos
        "Creación",
        "Edición",
        "Eliminación",
        "Cambio de estado",  # cambio de visibilidad
        "Cambio de tags",
        "Cambio de imágenes",  # para etapa 2
        # Para usuarios
        "Usuario creado",
        "Usuario actualizado",
        "Usuario bloqueado",
        "Usuario desbloqueado",
        "Rol asignado",
        "Contraseña cambiada",
        # Para propuestas (etapa 2)
        "Propuesta aprobada",
        "Propuesta rechazada",
        # Para reseñas (etapa 2)
        "Reseña aprobada",
        "Reseña rechazada",
    ]

    for event_name in event_types:
        event_type = EventType(name=event_name)
        db.session.add(event_type)

    db.session.commit()


def seed_system_admin():
    """Crea un usuario System Admin por defecto"""
    from core.models import User
    from core.services import role_service as RoleService

    print("Creando usuario System Admin...")

    # Obtener rol Administrador
    admin_role = RoleService.get_role_by_name("Administrador")

    # Crear usuario system admin
    admin_user = User(
        email="admin@sistema.com",
        first_name="System",
        last_name="Administrator",
        system_admin=True,
        active=True,
        role_id=admin_role.id,
    )
    admin_user.set_password("admin123")

    db.session.add(admin_user)
    db.session.commit()


def seed_feature_flags():
    """Crea los feature flags iniciales del sistema"""
    from src.core.models.feature_flag import FeatureFlag

    print("Creando feature flags...")

    # Feature flags según el documento del TI
    flags = [
        {
            "name": "admin_maintenance_mode",
            "description": "Modo mantenimiento del área de administración",
            "is_enabled": False,
            "maintenance_message": "El sistema de administración está en mantenimiento. Intente más tarde.",
        },
        {
            "name": "portal_maintenance_mode",
            "description": "Modo mantenimiento del portal público",
            "is_enabled": False,
            "maintenance_message": "El portal está en mantenimiento. Disculpe las molestias.",
        },
        {
            "name": "reviews_enabled",
            "description": "Habilitar creación y visualización de reseñas",
            "is_enabled": True,
            "maintenance_message": None,
        },
    ]

    for flag_data in flags:
        flag = FeatureFlag(
            name=flag_data["name"],
            description=flag_data["description"],
            is_enabled=flag_data["is_enabled"],
            maintenance_message=flag_data["maintenance_message"],
        )
        db.session.add(flag)

    db.session.commit()
