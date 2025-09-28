from core.database import db


def run():
    """Ejecuta todos los seeds en orden"""
    print("Iniciando seeders...")

    seed_permissions()
    seed_roles()
    # seed_event_types()
    seed_system_admin()
    seed_editor()
    seed_feature_flags()
    seed_tags()
    seed_provinces_and_cities()
    seed_consevation_states()
    seed_categories()
    seed_historic_sites()
    seed_site_tags()
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
            # Sitios
            "site_index",
            "site_new",
            "site_update",
            "site_show",
            "site_history",
            # Tags
            "tag_index",
            "tag_new",
            "tag_update",
            "tag_destroy",
            "tag_show",
            # Propuestas
            "proposal_index",
            "proposal_show",
            "proposal_approve",
            "proposal_reject",
            # Reseñas
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
            "user_change_password",
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
            # Propuestas
            "proposal_index",
            "proposal_show",
            "proposal_approve",
            "proposal_reject",
            # Reseñas
            "review_index",
            "review_show",
            "review_approve",
            "review_reject",
        ],
        "Usuario público": [
            "review_new",
            "proposal_new",
        ],
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
        password="admin123",
        email="admin@sistema.com",
        first_name="System",
        last_name="Administrator",
        system_admin=True,
        active=True,
        role_id=admin_role.id,
    )

    db.session.add(admin_user)
    db.session.commit()


def seed_editor():
    """Crea un usuario editor"""
    from core.models import User
    from core.services import role_service as RoleService

    print("Creando usuario editor...")

    # Obtener rol Editor
    editor_role = RoleService.get_role_by_name("Editor")

    # Crear usuario editor
    editor_user = User(
        password="editor123",
        email="editor_editor@hotmail.com",
        first_name="EditorNomb",
        last_name="EditorApe",
        system_admin=False,
        active=True,
        role_id=editor_role.id,
    )

    db.session.add(editor_user)
    db.session.commit()


def seed_feature_flags():
    """Crea los feature flags iniciales del sistema"""
    from core.models import FeatureFlag

    print("Creando feature flags...")

    # Feature flags según el documento del TI
    flags = [
        {
            "name": "admin_maintenance_mode",
            "description": "Modo mantenimiento del área de administración",
            "is_enabled": False,
            "maintenance_message": "",
        },
        {
            "name": "portal_maintenance_mode",
            "description": "Modo mantenimiento del portal público",
            "is_enabled": False,
            "maintenance_message": "",
        },
        {
            "name": "reviews_enabled",
            "description": "Habilitar creación y visualización de reseñas",
            "is_enabled": True,
            "maintenance_message": "No se permiten reseñas",
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


def seed_tags():
    from core.models import Tag

    print("Creando tags...")
    tags = ["Colonial", "Patrimonial", "tag 3", "tag 4"]

    for t in tags:
        tag = Tag(name=t)
        db.session.add(tag)
    db.session.commit()


def seed_provinces_and_cities():
    from core.models import City, Province

    print("Creando provincias y ciudades")

    # Provincias
    buenos_aires = Province(name="Buenos Aires")
    cordoba = Province(name="Córdoba")
    mendoza = Province(name="Mendoza")

    db.session.add_all([buenos_aires, cordoba, mendoza])
    db.session.commit()

    # Ciudades
    cities = [
        City(name="La Plata", province_id=buenos_aires.id),
        City(name="Mar del Plata", province_id=buenos_aires.id),
        City(name="Córdoba Capital", province_id=cordoba.id),
        City(name="Villa Carlos Paz", province_id=cordoba.id),
        City(name="Mendoza Capital", province_id=mendoza.id),
        City(name="San Rafael", province_id=mendoza.id),
    ]

    db.session.add_all(cities)
    db.session.commit()


def seed_consevation_states():
    from core.models import ConservationState

    print("Creando estados de conservacion...")
    states = [
        ConservationState(state="Bueno"),
        ConservationState(state="Regular"),
        ConservationState(state="Malo"),
    ]

    db.session.add_all(states)
    db.session.commit()


def seed_categories():
    from core.models import Category

    print("Cargando categorias...")

    categories = [
        Category(name="Arquitectura"),
        Category(name="Infraestructura"),
        Category(name="Sitio arqueológico"),
    ]

    db.session.add_all(categories)
    db.session.commit()


def seed_historic_sites():
    from datetime import datetime, timezone

    from core.models import HistoricSite

    print("Cargando sitios historicos...")
    sites = [
        HistoricSite(
            name="Cabildo de Buenos Aires",
            brief_description="Edificio histórico del periodo colonial.",
            full_description="El Cabildo de Buenos Aires fue sede de las autoridades coloniales. "
            "Actualmente funciona como museo, ubicado frente a la Plaza de Mayo.",
            latitude=-34.6083,
            longitude=-58.3712,
            inauguration_year=1610,
            registration_date=datetime.now(timezone.utc),
            is_visible=False,
            pending_validation=True,
            city_id=1,
            category_id=1,
            conservation_state_id=1,
            proposed_by=1,
        ),
        HistoricSite(
            name="Ruinas de San Ignacio Miní",
            brief_description="Misión jesuítica guaraní en Misiones.",
            full_description="Las Ruinas de San Ignacio Miní son Patrimonio de la Humanidad por la UNESCO "
            "y muestran el legado de las misiones jesuíticas en Argentina.",
            latitude=-27.2556,
            longitude=-55.5353,
            inauguration_year=1632,
            registration_date=datetime.now(timezone.utc),
            is_visible=False,
            pending_validation=True,
            city_id=2,
            category_id=2,
            conservation_state_id=2,
            proposed_by=1,
        ),
        HistoricSite(
            name="Teatro Colón",
            brief_description="Principal teatro de ópera de Argentina.",
            full_description="Inaugurado en 1908, el Teatro Colón es considerado uno de los cinco mejores del mundo "
            "por su acústica y su trayectoria artística.",
            latitude=-34.6012,
            longitude=-58.3836,
            inauguration_year=1908,
            registration_date=datetime.now(timezone.utc),
            is_visible=False,
            pending_validation=True,
            city_id=1,
            category_id=3,
            conservation_state_id=1,
            proposed_by=2,
        ),
    ]

    db.session.add_all(sites)

    db.session.commit()


def seed_site_tags():
    from core.services import historic_site_service as HistorcService
    from core.services import tag_service as TagService

    print("Agregando relaciones Sites-Tags")

    cabildo = HistorcService.get_historic_site_by_id(1)
    san_ignacio = HistorcService.get_historic_site_by_id(2)

    tag1 = TagService.get_tag_by_id(1)
    tag2 = TagService.get_tag_by_id(2)

    cabildo.tags.append(tag1)
    san_ignacio.tags.extend([tag1, tag2])

    db.session.commit()
