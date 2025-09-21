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
        ("user_index", "Listar usuarios"),
        ("user_new", "Crear usuario"),
        ("user_update", "Actualizar usuario"),
        ("user_destroy", "Eliminar usuario"),
        ("user_show", "Ver detalle de usuario"),
        ("user_block", "Bloquear/desbloquear usuario"),
        ("user_assign_role", "Asignar roles"),
    ]

    # Permisos para sitios históricos
    site_permissions = [
        ("site_index", "Listar sitios"),
        ("site_new", "Crear sitio"),
        ("site_update", "Actualizar sitio"),
        ("site_destroy", "Eliminar sitio"),
        ("site_show", "Ver detalle de sitio"),
        ("site_export", "Exportar sitios"),
        ("site_history", "Ver historial de sitio"),
    ]

    # Permisos para tags
    tag_permissions = [
        ("tag_index", "Listar tags"),
        ("tag_new", "Crear tag"),
        ("tag_update", "Actualizar tag"),
        ("tag_destroy", "Eliminar tag"),
        ("tag_show", "Ver detalle de tag"),
    ]

    # Permisos para feature flags (solo System Admin)
    flag_permissions = [
        ("flag_index", "Listar feature flags"),
        ("flag_update", "Actualizar feature flags"),
    ]

    # Permisos para validación de propuestas (Etapa 2)
    proposal_permissions = [
        ("proposal_index", "Listar propuestas"),
        ("proposal_show", "Ver propuesta"),
        ("proposal_approve", "Aprobar propuesta"),
        ("proposal_reject", "Rechazar propuesta"),
    ]

    # Permisos para moderación de reseñas (Etapa 2)
    review_permissions = [
        ("review_index", "Listar reseñas"),
        ("review_show", "Ver reseña"),
        ("review_approve", "Aprobar reseña"),
        ("review_reject", "Rechazar reseña"),
    ]

    all_permissions = (
        user_permissions
        + site_permissions
        + tag_permissions
        + flag_permissions
        + proposal_permissions
        + review_permissions
    )

    # Transformar la lista de tuplas en la lista de dicts que espera create_multiple_permissions
    permissions_data = [
        {"name": name, "description": desc} for name, desc in all_permissions
    ]

    PermissionService.create_multiple_permissions(permissions_data)


def seed_roles():
    """Crea los roles del sistema según los requerimientos del TI"""
    from core.models import Permission
    from core.services import role_service as RoleService

    print("Creando roles...")

    # Obtener todos los permisos
    all_permissions = Permission.query.all()

    roles_permissions = {
        "Editor": [
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
        ],
        "Administrador": [
            # Usuarios
            "user_index",
            "user_new",
            "user_update",
            "user_destroy",
            "user_show",
            "user_block",
            "user_assign_role",
            # Sitios
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
        ],
        "Usuario público": [],  # TODO: Ver bien qué permisos tiene
    }

    for role_name, perm_names in roles_permissions.items():
        # Obtener ID de los permisos
        permission_ids = [p.id for p in all_permissions if p.name in perm_names]

        if permission_ids:
            RoleService.create_role_with_permissions(role_name, permission_ids)
        else:
            RoleService.create_role_without_permissions(role_name)


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
