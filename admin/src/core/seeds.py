from geoalchemy2.elements import WKTElement

from core.database import db


def run(env="production"):
    """Ejecuta los seeders necesarios según el entorno.

    - Producción:
      Solo datos estrictamente necesarios (tags, provincias/ciudades, estados de conservación, categorías, feature_flags, usuario system admin).

    - Desarrollo:
      Además de lo anterior, incluye seeds de permisos, roles, editores, usuarios públicos, sitios históricos de ejemplo y relaciones con tags.
    """
    print("Iniciando seeders...")

    # Siempre en todos los entornos
    seed_permissions()
    seed_roles()
    seed_system_admin()
    seed_feature_flags()
    seed_tags()
    seed_provinces_and_cities()
    seed_consevation_states()
    seed_categories()
    seed_event_types()

    # Solo si estamos en development
    seed_aditional_public_users()
    seed_aditional_editors()
    seed_aditional_admins()
    seed_aditional_moderators()
    seed_historic_sites()
    seed_aditional_historic_sites()
    seed_aditional_validated_historic_sites()
    seed_site_tags()
    seed_favorites()
    seed_reviews()
    seed_pending_reviews()
    seed_rejected_reviews()
    seed_site_images_from_seed_folder()

    print("Seed finalizado")


def _recalculate_site_ratings(site_ids):
    """Recalcula el promedio y la cantidad de reseñas aprobadas para los sitios dados."""
    if not site_ids:
        return

    from sqlalchemy import func

    from core.models import HistoricSite, Review
    from core.models.review import ReviewStatus

    aggregates = (
        db.session.query(
            Review.historic_site_id,
            func.count(Review.id),
            func.avg(Review.rating),
        )
        .filter(
            Review.historic_site_id.in_(site_ids),
            Review.status == ReviewStatus.APROBADA,
        )
        .group_by(Review.historic_site_id)
        .all()
    )

    aggregate_map = {
        site_id: (count, float(avg) if avg is not None else 0.0)
        for site_id, count, avg in aggregates
    }

    for site in (
        db.session.query(HistoricSite).filter(HistoricSite.id.in_(site_ids)).all()
    ):
        count, average = aggregate_map.get(site.id, (0, 0.0))
        site.rating_count = count
        site.average_rating = average

    db.session.commit()


def seed_permissions():
    """Crea los permisos básicos del sistema siguiendo el patrón modulo_accion."""
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
        ("user_change_password", "Cambiar contraseña de usuario"),
    ]

    # Permisos para módulo de ciudades
    city_permissions = [
        ("city_index", "Listar ciudades"),
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
        ("site_restore", "Restaurar sitio borrado"),
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
        ("proposal_new", "Proponer nuevo sitio histórico"),
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
        ("review_new", "Crear reseña"),
        ("review_update", "Actualizar reseña"),
        ("review_destroy", "Eliminar reseña"),
    ]

    favorite_permissions = [
        ("favorite_index", "Listar sitios favoritos"),
        ("favorite_new", "Agregar sitio a favoritos"),
        ("favorite_destroy", "Eliminar sitio de favoritos"),
    ]

    all_permissions = (
        user_permissions
        + site_permissions
        + tag_permissions
        + flag_permissions
        + proposal_permissions
        + review_permissions
        + city_permissions
        + favorite_permissions
    )

    # Transformar la lista de tuplas en la lista de dicts que espera create_multiple_permissions
    permissions_data = [
        {"name": name, "description": desc} for name, desc in all_permissions
    ]

    PermissionService.create_multiple_permissions(permissions_data)


def seed_roles():
    """
    Crea los roles del sistema según los requerimientos del enunciado.
    Roles definidos:
    - Usuario público: puede proponer sitios y crear reseñas.
    - Editor: administra sitios, tags, propuestas y reseñas.
    - Administrador: incluye funciones de editor y además gestiona usuarios y roles.
    - Administrador del sistema:
        * Incluye todas las funciones del sistema y además gestión de feature flags.
        * Aunque este rol no se cargue, se identifica con un boolean en el modelo del usuario
    """
    from core.models import Permission
    from core.services import role_service as RoleService

    print("Creando roles...")

    # Obtener todos los permisos
    all_permissions = Permission.query.all()

    roles_permissions = {
        "Moderador": [
            # Reseñas
            "review_index",
            "review_show",
            "review_approve",
            "review_reject",
            "review_destroy",
        ],
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
            "review_destroy",
            # Ciudades
            "city_index",
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
            "site_restore",
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
            # Ciudades
            "city_index",
        ],
        "Usuario público": [
            # Reseñas
            "review_new",
            "review_update",
            "review_destroy",
            # Sitios
            "proposal_new",
            # Favoritos
            "favorite_index",
            "favorite_new",
            "favorite_destroy",
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
        "Restauración",
        "Cambio de estado",  # Cambio de visibilidad
        "Cambio de tags",
        "Cambio de imágenes",
    ]

    for event_name in event_types:
        event_type = EventType(name=event_name)
        db.session.add(event_type)

    db.session.commit()


def seed_system_admin():
    """
    Crea un usuario System Admin por defecto
    Este usuario tiene:
    - Rol Administrador.
    - Acceso total al sistema.
    - Email: admin@sistema.com
    - Contraseña: admin123
    """
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
        role_id=admin_role.id,
    )

    db.session.add(admin_user)
    db.session.commit()


def seed_feature_flags():
    """Crea los feature flags iniciales del sistema.

    Flags incluidos:
    - admin_maintenance_mode: Modo mantenimiento del área de administración.
    - portal_maintenance_mode: Modo mantenimiento del portal público.
    - reviews_enabled: Controla la creación y visualización de reseñas.
    """
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
    """Crea un conjunto inicial de tags para clasificar sitios históricos"""
    from slugify import slugify

    from core.models import Tag

    print("Creando tags...")
    tags = [
        "Colonial",
        "Patrimonial",
        "Arqueológico",
        "Industrial",
        "Religioso",
        "Educativo",
        "Cultural",
        "Militar",
        "Arquitectónico",
        "Natural",
        "Turístico",
        "Histórico",
        "Museístico",
        "Monumental",
        "Artístico",
        "Político",
        "Cívico",
        "Comunitario",
        "Inmueble protegido",
        "Independencia",
        "Precolombino",
        "Jesuítico",
        "Rural",
        "Urbano",
        "Emblemático",
        "Contemporáneo",
        "Tradicional",
    ]

    for t in tags:
        tag = Tag(name=t, slug=slugify(t))
        db.session.add(tag)

    db.session.commit()


def seed_provinces_and_cities():
    """Crea las 24 provincias de Argentina y sus ciudades usando relaciones"""
    from core.models import City, Province

    print("Creando provincias y ciudades de Argentina")

    provinces_data = [
        ("Buenos Aires", ["La Plata", "Mar del Plata"]),
        ("Catamarca", ["San Fernando del Valle de Catamarca", "Andalgalá"]),
        ("Chaco", ["Resistencia", "Presidencia Roque Sáenz Peña"]),
        ("Chubut", ["Rawson", "Comodoro Rivadavia"]),
        ("Córdoba", ["Córdoba Capital", "Villa Carlos Paz"]),
        ("Corrientes", ["Corrientes", "Goya"]),
        ("Entre Ríos", ["Paraná", "Concordia"]),
        ("Formosa", ["Formosa", "Clorinda"]),
        ("Jujuy", ["San Salvador de Jujuy", "San Pedro de Jujuy"]),
        ("La Pampa", ["Santa Rosa", "General Pico"]),
        ("La Rioja", ["La Rioja", "Chilecito"]),
        ("Mendoza", ["Mendoza", "San Rafael"]),
        ("Misiones", ["Posadas", "Puerto Iguazú"]),
        ("Neuquén", ["Neuquén", "San Martín de los Andes"]),
        ("Río Negro", ["Viedma", "Bariloche"]),
        ("Salta", ["Salta", "San Ramón de la Nueva Orán"]),
        ("San Juan", ["San Juan", "Caucete"]),
        ("San Luis", ["San Luis", "Villa Mercedes"]),
        ("Santa Cruz", ["Río Gallegos", "Caleta Olivia"]),
        ("Santa Fe", ["Santa Fe", "Rosario"]),
        ("Santiago del Estero", ["Santiago del Estero", "La Banda"]),
        (
            "Tierra del Fuego, Antártida e Islas del Atlántico Sur",
            ["Ushuaia", "Río Grande"],
        ),
        ("Tucumán", ["San Miguel de Tucumán", "Tafí Viejo"]),
    ]

    # Crear todo en una sola transacción
    for province_name, city_names in provinces_data:
        province = Province(name=province_name)
        db.session.add(province)
        db.session.flush()  # Para obtener el ID sin hacer commit

        for city_name in city_names:
            city = City(name=city_name, province=province)
            db.session.add(city)

    db.session.commit()


def seed_consevation_states():
    """Crea los estados de conservación posibles para los sitios históricos"""
    from core.models import ConservationState

    print("Creando estados de conservacion...")
    states = [
        ConservationState(state="Excelente"),
        ConservationState(state="Bueno"),
        ConservationState(state="Regular"),
        ConservationState(state="Malo"),
    ]

    db.session.add_all(states)
    db.session.commit()


def seed_categories():
    """Crea las categorías iniciales de los sitios históricos"""
    from core.models import Category

    print("Creando categorias...")

    categories = [
        Category(name="Arquitectura"),
        Category(name="Infraestructura"),
        Category(name="Sitio arqueológico"),
        Category(name="Museo"),
        Category(name="Monumento"),
        Category(name="Iglesia"),
        Category(name="Espacio público"),
        Category(name="Edificio gubernamental"),
        Category(name="Centro cultural"),
        Category(name="Residencia histórica"),
        Category(name="Parque"),
        Category(name="Cementerio histórico"),
        Category(name="Fortificación"),
        Category(name="Estancia"),
        Category(name="Escuela"),
        Category(name="Puente"),
        Category(name="Faro"),
        Category(name="Estación ferroviaria"),
        Category(name="Obra escultórica"),
    ]

    db.session.add_all(categories)
    db.session.commit()


def seed_historic_sites():
    """Carga un conjunto de sitios históricos iniciales"""
    from datetime import datetime, timezone

    from core.audit import disable_audit_listeners, enable_audit_listeners
    from core.models import HistoricSite

    print("Cargando sitios historicos...")

    # Deshabilitar registros de auditoría temporalmente
    disable_audit_listeners()

    sites = [
        HistoricSite(
            name="Cabildo de Buenos Aires",
            brief_description="Edificio histórico del periodo colonial.",
            full_description="El Cabildo de Buenos Aires fue sede de las autoridades coloniales. "
            "Actualmente funciona como museo, ubicado frente a la Plaza de Mayo.",
            inauguration_year=1610,
            created_at=datetime.now(timezone.utc),
            is_visible=False,
            pending_validation=True,
            city_id=1,
            category_id=1,
            conservation_state_id=1,
            proposed_by=1,
            location=WKTElement("POINT(-57.9561 -34.9226)"),
        ),
        HistoricSite(
            name="Ruinas de San Ignacio Miní",
            brief_description="Misión jesuítica guaraní en Misiones.",
            full_description="Las Ruinas de San Ignacio Miní son Patrimonio de la Humanidad por la UNESCO "
            "y muestran el legado de las misiones jesuíticas en Argentina.",
            inauguration_year=1632,
            created_at=datetime.now(timezone.utc),
            is_visible=False,
            pending_validation=True,
            city_id=2,
            category_id=2,
            conservation_state_id=2,
            proposed_by=1,
            location=WKTElement("POINT(-57.9319 -34.9085)"),
        ),
        HistoricSite(
            name="Teatro Colón",
            brief_description="Principal teatro de ópera de Argentina.",
            full_description="Inaugurado en 1908, el Teatro Colón es considerado uno de los cinco mejores del mundo "
            "por su acústica y su trayectoria artística.",
            inauguration_year=1908,
            created_at=datetime.now(timezone.utc),
            is_visible=False,
            pending_validation=True,
            city_id=1,
            category_id=3,
            conservation_state_id=1,
            proposed_by=2,
            location=WKTElement("POINT(-57.9543 -34.9216)"),
        ),
        HistoricSite(
            name="Estancia Jesuítica de Alta Gracia",
            brief_description="Patrimonio de la Humanidad en Córdoba.",
            full_description="La Estancia Jesuítica de Alta Gracia, declarada Patrimonio de la Humanidad por la UNESCO, "
            "incluye una iglesia y un museo que reflejan la historia jesuítica en Argentina.",
            inauguration_year=1643,
            created_at=datetime.now(timezone.utc),
            is_visible=False,
            pending_validation=True,
            city_id=3,
            category_id=2,
            conservation_state_id=2,
            proposed_by=2,
            location=WKTElement("POINT(-64.1950 -31.6375)"),
        ),
        HistoricSite(
            name="Parque General San Martín",
            brief_description="Gran parque urbano en Mendoza.",
            full_description="El Parque General San Martín es un extenso espacio verde en Mendoza, "
            "diseñado por el paisajista Carlos Thays, ideal para actividades recreativas y culturales.",
            inauguration_year=1896,
            created_at=datetime.now(timezone.utc),
            is_visible=False,
            pending_validation=True,
            city_id=5,
            category_id=1,
            conservation_state_id=1,
            proposed_by=1,
            location=WKTElement("POINT(-68.8470 -32.8903)"),
        ),
        HistoricSite(
            name="Puente del Inca",
            brief_description="Formación natural y sitio histórico en Mendoza.",
            full_description="El Puente del Inca es una formación natural que sirvió como paso incaico y "
            "lugar de baños termales, con una historia que data de la época precolombina.",
            inauguration_year=0,
            created_at=datetime.now(timezone.utc),
            is_visible=False,
            pending_validation=True,
            city_id=5,
            category_id=2,
            conservation_state_id=3,
            proposed_by=2,
            location=WKTElement("POINT(-69.6605 -32.6532)"),
        ),
        HistoricSite(
            name="Casa del Virrey Liniers",
            brief_description="Residencia histórica en Buenos Aires.",
            full_description="La Casa del Virrey Liniers, construida en el siglo XVIII, es un ejemplo "
            "destacado de la arquitectura colonial y fue residencia del virrey Santiago de Liniers.",
            inauguration_year=1784,
            created_at=datetime.now(timezone.utc),
            is_visible=False,
            pending_validation=True,
            city_id=1,
            category_id=1,
            conservation_state_id=2,
            proposed_by=1,
            location=WKTElement("POINT(-57.9530 -34.9212)"),
        ),
        HistoricSite(
            name="Museo Nacional de Bellas Artes",
            brief_description="Principal museo de arte en Argentina.",
            full_description="El Museo Nacional de Bellas Artes alberga una vasta colección de arte argentino "
            "e internacional, siendo un centro cultural clave en Buenos Aires.",
            inauguration_year=1895,
            created_at=datetime.now(timezone.utc),
            is_visible=False,
            pending_validation=True,
            city_id=1,
            category_id=3,
            conservation_state_id=1,
            proposed_by=2,
            location=WKTElement("POINT(-57.5780 -34.5883)"),
        ),
        HistoricSite(
            name="Iglesia de la Compañía de Jesús",
            brief_description="Iglesia barroca en Córdoba.",
            full_description="La Iglesia de la Compañía de Jesús, construida en el siglo XVIII, es un "
            "ejemplo destacado del barroco colonial y forma parte del conjunto histórico jesuítico de Córdoba.",
            inauguration_year=1670,
            created_at=datetime.now(timezone.utc),
            is_visible=False,
            pending_validation=True,
            city_id=3,
            category_id=1,
            conservation_state_id=2,
            proposed_by=1,
            location=WKTElement("POINT(-64.1811 -31.4135)"),
        ),
        HistoricSite(
            name="Cerro de la Gloria",
            brief_description="Monumento histórico en Mendoza.",
            full_description="El Cerro de la Gloria es un monumento dedicado a los héroes de la independencia argentina, "
            "ubicado en el Parque General San Martín.",
            inauguration_year=1914,
            created_at=datetime.now(timezone.utc),
            is_visible=False,
            pending_validation=True,
            city_id=5,
            category_id=1,
            conservation_state_id=1,
            proposed_by=2,
            location=WKTElement("POINT(-68.8475 -32.8900)"),
        ),
        HistoricSite(
            name="Casa de Tucumán",
            brief_description="Lugar histórico de la independencia argentina.",
            full_description="La Casa de Tucumán es el sitio donde se declaró la independencia de Argentina en 1816, "
            "y actualmente funciona como museo.",
            inauguration_year=1760,
            created_at=datetime.now(timezone.utc),
            is_visible=False,
            pending_validation=True,
            city_id=4,
            category_id=1,
            conservation_state_id=2,
            proposed_by=1,
            location=WKTElement("POINT(-65.2176 -26.8083)"),
        ),
        HistoricSite(
            name="Monumento a la Bandera",
            brief_description="Monumento emblemático en Rosario.",
            full_description="El Monumento a la Bandera en Rosario es un símbolo nacional que conmemora la creación "
            "de la bandera argentina por Manuel Belgrano.",
            inauguration_year=1957,
            created_at=datetime.now(timezone.utc),
            is_visible=False,
            pending_validation=True,
            city_id=6,
            category_id=1,
            conservation_state_id=1,
            proposed_by=2,
            location=WKTElement("POINT(-60.6393 -32.9468)"),
        ),
        HistoricSite(
            name="Obelisco de Buenos Aires",
            brief_description="Monumento icónico de la ciudad.",
            full_description="El Obelisco es uno de los monumentos más emblemáticos de Buenos Aires, inaugurado en 1936.",
            inauguration_year=1936,
            created_at=datetime.now(timezone.utc),
            is_visible=False,
            pending_validation=True,
            city_id=1,
            category_id=1,
            conservation_state_id=1,
            proposed_by=1,
            location=WKTElement("POINT(-58.3816 -34.6037)"),
        ),
        HistoricSite(
            name="Catedral de La Plata",
            brief_description="Catedral neogótica en La Plata.",
            full_description="La Catedral de La Plata es una de las iglesias más grandes de Argentina, de estilo neogótico.",
            inauguration_year=1932,
            created_at=datetime.now(timezone.utc),
            is_visible=False,
            pending_validation=True,
            city_id=1,
            category_id=1,
            conservation_state_id=1,
            proposed_by=2,
            location=WKTElement("POINT(-57.9545 -34.9211)"),
        ),
        HistoricSite(
            name="Museo de la Memoria",
            brief_description="Espacio de memoria en Rosario.",
            full_description="El Museo de la Memoria recuerda a las víctimas del terrorismo de Estado en Argentina.",
            inauguration_year=2004,
            created_at=datetime.now(timezone.utc),
            is_visible=False,
            pending_validation=True,
            city_id=6,
            category_id=3,
            conservation_state_id=1,
            proposed_by=1,
            location=WKTElement("POINT(-60.6430 -32.9470)"),
        ),
        HistoricSite(
            name="Basílica de Luján",
            brief_description="Santuario nacional de la Virgen de Luján.",
            full_description="La Basílica de Luján es uno de los principales centros de peregrinación católica del país.",
            inauguration_year=1935,
            created_at=datetime.now(timezone.utc),
            is_visible=False,
            pending_validation=True,
            city_id=1,
            category_id=1,
            conservation_state_id=1,
            proposed_by=2,
            location=WKTElement("POINT(-59.1042 -34.5421)"),
        ),
    ]

    db.session.add_all(sites)

    db.session.commit()

    # Rehabilitar listeners de auditoría
    enable_audit_listeners()


def seed_site_tags():
    """Asigna entre una y cinco tags aleatorias a cada sitio histórico."""

    from random import randint, sample

    from core.audit import disable_audit_listeners, enable_audit_listeners
    from core.models import HistoricSite, Tag

    print("Asignando tags aleatorias a sitios historicos...")

    tags = Tag.query.all()
    sites = HistoricSite.query.all()

    if not sites:
        print("No hay sitios historicos para asignar tags.")
        return

    if not tags:
        print("No hay tags disponibles para asignar.")
        return

    max_tags = min(5, len(tags))

    disable_audit_listeners()

    try:
        for site in sites:
            site.tags.clear()
            count = randint(1, max_tags)
            selected_tags = sample(tags, count)
            site.tags.extend(selected_tags)

        db.session.commit()
    finally:
        enable_audit_listeners()


def seed_aditional_public_users():
    """Crea usuarios públicos adicionales (portal)"""
    import uuid

    from faker import Faker

    from core.models import User
    from core.services import role_service as RoleService

    print("Creando usuarios públicos adicionales...")
    fake = Faker("es_AR")

    role_public = RoleService.get_role_by_name("Usuario público")

    usuarios = [
        User(
            email=f"{uuid.uuid4().hex[:8]}_{fake.user_name()}@example.com",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            password="password123",
            role_id=role_public.id,
            system_admin=False,
        )
        for _ in range(100)
    ]

    db.session.add_all(usuarios)
    db.session.commit()


def seed_aditional_editors():
    """Crea usuarios editores adicionales"""
    import uuid

    from faker import Faker

    from core.models import User
    from core.services import role_service as RoleService

    print("Creando usuarios editores adicionales...")
    fake = Faker("es_AR")

    role_editor = RoleService.get_role_by_name("Editor")

    usuarios = [
        User(
            email=f"{uuid.uuid4().hex[:8]}_{fake.user_name()}@example.com",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            password="editor123",
            role_id=role_editor.id,
            system_admin=False,
        )
        for _ in range(30)
    ]

    db.session.add_all(usuarios)
    db.session.commit()


def seed_aditional_admins():
    """Crea usuarios administradores adicionales (no system admin)"""
    import uuid

    from faker import Faker

    from core.models import User
    from core.services import role_service as RoleService

    print("Creando usuarios administradores adicionales...")
    fake = Faker("es_AR")

    role_admin = RoleService.get_role_by_name("Administrador")

    usuarios = [
        User(
            email=f"{uuid.uuid4().hex[:8]}_{fake.user_name()}@example.com",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            password="admin123",
            role_id=role_admin.id,
            system_admin=False,
        )
        for _ in range(20)
    ]

    db.session.add_all(usuarios)
    db.session.commit()


def seed_aditional_moderators():
    """Crea usuarios moderadores adicionales"""
    import uuid

    from faker import Faker

    from core.models import User
    from core.services import role_service as RoleService

    print("Creando usuarios moderadores adicionales...")
    fake = Faker("es_AR")

    role_moderator = RoleService.get_role_by_name("Moderador")

    usuarios = [
        User(
            email=f"{uuid.uuid4().hex[:8]}_{fake.user_name()}@example.com",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            password="moderador123",
            role_id=role_moderator.id,
            system_admin=False,
        )
        for _ in range(50)
    ]

    db.session.add_all(usuarios)
    db.session.commit()


def seed_aditional_historic_sites():
    """
    Crea sitios históricos adicionales con Faker para desarrollo.
    Genera ubicaciones aleatorias dentro de provincias existentes.
    """
    from datetime import datetime, timezone
    from random import choice, randint, uniform

    from faker import Faker
    from geoalchemy2.elements import WKTElement

    from core.audit import disable_audit_listeners, enable_audit_listeners
    from core.models import Category, City, ConservationState, HistoricSite, User

    print("Creando sitios históricos adicionales con Faker...")

    fake = Faker("es_AR")
    disable_audit_listeners()

    cities = City.query.all()
    categories = Category.query.all()
    states = ConservationState.query.all()
    users = User.query.filter_by(system_admin=False).all()

    if not (cities and categories and states and users):
        print("No hay datos base suficientes para generar sitios adicionales.")
        return

    sitios = []
    for _ in range(100):
        city = choice(cities)
        category = choice(categories)
        state = choice(states)
        user = choice(users)

        # Coordenadas aleatorias dentro del rango general de Argentina
        lon = round(uniform(-73, -53), 6)
        lat = round(uniform(-55, -21), 6)

        sitios.append(
            HistoricSite(
                name=f"Sitio histórico {fake.city()}",
                brief_description=fake.sentence(nb_words=10)[:50],
                full_description=fake.paragraph(nb_sentences=4),
                inauguration_year=randint(1600, 2020),
                created_at=datetime.now(timezone.utc),
                is_visible=False,
                pending_validation=True,
                city_id=city.id,
                category_id=category.id,
                conservation_state_id=state.id,
                proposed_by=user.id,
                location=WKTElement(f"POINT({lon} {lat})", srid=4326),
            )
        )

    db.session.add_all(sitios)
    db.session.commit()
    enable_audit_listeners()


def seed_aditional_validated_historic_sites():
    """
    Crea sitios históricos adicionales validados, con Faker para desarrollo.
    Genera ubicaciones aleatorias dentro de provincias existentes.
    """
    from datetime import datetime, timezone
    from random import choice, randint, uniform

    from faker import Faker
    from geoalchemy2.elements import WKTElement

    from core.audit import disable_audit_listeners, enable_audit_listeners
    from core.models import Category, City, ConservationState, HistoricSite, User

    print("Creando sitios históricos validados con Faker...")

    fake = Faker("es_AR")
    disable_audit_listeners()

    cities = City.query.all()
    categories = Category.query.all()
    states = ConservationState.query.all()
    users = User.query.filter_by(system_admin=False).all()

    if not (cities and categories and states and users):
        print("No hay datos base suficientes para generar sitios validados.")
        return

    # Tipos de sitios históricos argentinos
    tipos_sitio = [
        # Cabildos y edificios coloniales
        "Cabildo Histórico de",
        "Antiguo Cabildo de",
        "Ex Cabildo Colonial de",

        # Iglesias y templos
        "Iglesia Nuestra Señora del Rosario de",
        "Basílica de San Francisco de",
        "Capilla del Carmen de",
        "Iglesia de Santo Domingo de",
        "Parroquia Nuestra Señora de la Merced de",
        "Iglesia de San Ignacio de",
        "Catedral Metropolitana de",
        "Convento de San Bernardo de",
        "Iglesia de la Compañía de Jesús de",
        "Capilla de Santa Ana de",
        "Basílica del Santísimo Sacramento de",

        # Casas históricas
        "Casa Histórica de",
        "Casa Colonial de",
        "Residencia Histórica de",
        "Casa de Gobierno de",
        "Quinta Histórica de",
        "Casa Natal de Sarmiento en",
        "Antigua Residencia de",

        # Estancias
        "Estancia Santa Catalina de",
        "Estancia Jesús María de",
        "Estancia La Candelaria de",
        "Estancia San Ignacio de",
        "Estancia Colonial de",

        # Fortines y construcciones militares
        "Fortín Independencia de",
        "Fortín Colonial de",
        "Reducto Histórico de",
        "Fuerte de",
        "Cuartel Histórico de",

        # Teatros
        "Teatro Municipal de",
        "Teatro del Libertador General San Martín de",
        "Teatro Coliseo de",
        "Teatro Provincial de",
        "Teatro Independencia de",

        # Estaciones de tren
        "Estación Central de Ferrocarril de",
        "Antigua Estación del Tren de",
        "Estación Ferroviaria de",
        "Estación del Ferrocarril Mitre de",

        # Plazas y espacios públicos
        "Plaza 25 de Mayo de",
        "Plaza de la Independencia de",
        "Plaza San Martín de",
        "Plaza 9 de Julio de",
        "Plaza Belgrano de",
        "Plaza Moreno de",

        # Molinos y construcciones rurales
        "Molino Harinero de",
        "Antiguo Molino de",
        "Tahona Colonial de",

        # Monumentos
        "Monumento a los Caídos de",
        "Monumento al General San Martín de",
        "Obelisco de",
        "Pirámide de Mayo de",

        # Bodegas (principalmente para Mendoza, San Juan)
        "Bodega Histórica de",
        "Antigua Bodega de",

        # Museos
        "Museo Histórico Municipal de",
        "Museo de Bellas Artes de",
        "Museo Provincial de",

        # Otros
        "Aduana Histórica de",
        "Correo Central de",
        "Banco Provincial de",
        "Palacio Municipal de",
        "Mercado de Abasto de",
        "Pulpería Histórica de",
        "Cementerio Municipal de",
        "Puente Colgante de",
        "Dique de",
        "Confitería del Molino de"
    ]

    sitios = []
    for _ in range(100):
        city = choice(cities)
        category = choice(categories)
        state = choice(states)
        user = choice(users)

        # Concatenar tipo de sitio + nombre de ciudad
        tipo = choice(tipos_sitio)
        nombre = f"{tipo}{city.name}"

        # Coordenadas aleatorias dentro del rango general de Argentina
        lon = round(uniform(-73, -53), 6)
        lat = round(uniform(-55, -21), 6)

        sitios.append(
            HistoricSite(
                name=nombre,
                brief_description=fake.sentence(nb_words=10)[:50],
                full_description=fake.paragraph(nb_sentences=4),
                inauguration_year=randint(1600, 2020),
                created_at=datetime.now(timezone.utc),
                is_visible=True,
                pending_validation=False,
                city_id=city.id,
                category_id=category.id,
                conservation_state_id=state.id,
                proposed_by=user.id,
                location=WKTElement(f"POINT({lon} {lat})", srid=4326),
            )
        )

    db.session.add_all(sitios)
    db.session.commit()
    enable_audit_listeners()


def seed_reviews():
    """Genera entre 1 y 10 reseñas aprobadas para cada sitio histórico publicado."""
    import random
    from datetime import datetime, timezone

    from faker import Faker

    from core.audit import disable_audit_listeners, enable_audit_listeners
    from core.models import Review, User
    from core.models.review import ReviewStatus
    from core.services.historic_site_service import get_published_historic_sites

    print("Generando reseñas aprobadas para sitios publicados...")

    fake = Faker("es_AR")

    sites = get_published_historic_sites()
    if not sites:
        print("No hay sitios publicados para generar reseñas.")
        return

    public_users = User.query.join(User.role).filter_by(name="Usuario público").all()
    if not public_users:
        print("No hay usuarios públicos para generar reseñas.")
        return

    disable_audit_listeners()

    reviews = []
    try:
        for site in sites:
            max_possible = min(10, len(public_users))

            if max_possible < 10:
                review_count = max_possible
            else:
                review_count = random.randint(10, max_possible)

            reviewers = random.sample(public_users, review_count)

            for user in reviewers:
                timestamp = fake.date_time_between(
                    start_date="-2y", end_date="now", tzinfo=timezone.utc
                )
                reviews.append(
                    Review(
                        rating=random.randint(1, 5),
                        content=fake.paragraph(nb_sentences=random.randint(2, 4)),
                        status=ReviewStatus.APROBADA,
                        user_id=user.id,
                        historic_site_id=site.id,
                        created_at=timestamp,
                        updated_at=timestamp,
                    )
                )

        if not reviews:
            print("No se generaron reseñas para los sitios publicados.")
            return

        db.session.add_all(reviews)
        db.session.commit()

        _recalculate_site_ratings([site.id for site in sites])
    finally:
        enable_audit_listeners()


def seed_favorites():
    """Asocia aleatoriamente sitios históricos a usuarios públicos como favoritos."""
    from random import randint, sample

    from core.audit import disable_audit_listeners, enable_audit_listeners
    from core.models import HistoricSite, User

    print("Agregando favoritos de usuarios...")

    # Deshabilitar registros de auditoría temporalmente
    disable_audit_listeners()

    # Solo usuarios públicos
    public_users = User.query.join(User.role).filter_by(name="Usuario público").all()
    sites = HistoricSite.query.all()

    if not public_users or not sites:
        print("No hay usuarios o sitios para generar favoritos.")
        return

    count = 0
    for user in public_users:
        # Cada usuario marcará entre 2 y 5 sitios como favoritos
        num_favorites = randint(2, 5)
        chosen_sites = sample(sites, min(num_favorites, len(sites)))

        for site in chosen_sites:
            if site not in user.favorite_sites:
                user.favorite_sites.append(site)
                count += 1

    from core.database import db

    db.session.commit()

    # Rehabilitar listeners de auditoría
    enable_audit_listeners()


def seed_site_images_from_seed_folder():
    """Asigna tres imágenes aleatorias desde la carpeta de seeds a cada sitio histórico."""

    from contextlib import ExitStack
    from pathlib import Path
    from random import sample

    from werkzeug.datastructures import FileStorage

    from core.audit import disable_audit_listeners, enable_audit_listeners
    from core.models import HistoricSite
    from core.services import site_image_service

    print("Asignando imagenes aleatorias a sitios historicos...")

    disable_audit_listeners()

    try:
        images_folder = (
            Path(__file__).resolve().parents[2]
            / "static"
            / "img"
            / "images for seeding"
        )

        if not images_folder.exists():
            print(
                "No se encontro la carpeta de imagenes para seeds en 'static/img/images for seeding'."
            )
            return

        image_files = [path for path in images_folder.iterdir() if path.is_file()]

        if not image_files:
            print("No hay imagenes disponibles para asignar a los sitios historicos.")
            return

        sites = HistoricSite.query.all()

        if not sites:
            print("No hay sitios historicos para asignar imagenes.")
            return

        image_count = min(3, len(image_files))

        for site in sites:
            site_image_service.delete_all_site_images(site.id)

            selected_images = sample(image_files, image_count)

            with ExitStack() as stack:
                files = []
                titles = []

                for index, image_path in enumerate(selected_images):
                    file_handle = stack.enter_context(image_path.open("rb"))
                    file_storage = FileStorage(
                        stream=file_handle, filename=image_path.name
                    )
                    file_storage.stream.seek(0)

                    files.append(file_storage)
                    titles.append(f"{site.name} - Imagen {index + 1}")

                site_image_service.create_multiple_images(
                    historic_site_id=site.id,
                    files=files,
                    set_first_as_cover=True,
                    titles=titles,
                )
    finally:
        enable_audit_listeners()


def seed_pending_reviews():
    """Genera cinco reseñas pendientes para 50 sitios históricos aleatorios."""
    import random
    from datetime import datetime, timezone

    from faker import Faker

    from core.audit import disable_audit_listeners, enable_audit_listeners
    from core.models import Review, User
    from core.models.review import ReviewStatus
    from core.services.historic_site_service import get_published_historic_sites

    print("Generando reseñas pendientes para moderación...")

    fake = Faker("es_AR")

    sites = get_published_historic_sites()
    if not sites:
        print("No hay sitios publicados para generar reseñas pendientes.")
        return

    public_users = User.query.join(User.role).filter_by(name="Usuario público").all()
    if not public_users:
        print("No hay usuarios públicos para generar reseñas pendientes.")
        return

    selected_sites = random.sample(sites, min(50, len(sites)))

    disable_audit_listeners()

    pending_reviews = []
    try:
        for site in selected_sites:
            existing_user_ids = {review.user_id for review in site.reviews}
            available_users = [
                user for user in public_users if user.id not in existing_user_ids
            ]

            if not available_users:
                continue

            reviewers = random.sample(available_users, min(5, len(available_users)))

            for user in reviewers:
                timestamp = fake.date_time_between(
                    start_date="-6m", end_date="now", tzinfo=timezone.utc
                )
                pending_reviews.append(
                    Review(
                        rating=random.randint(1, 5),
                        content=fake.paragraph(nb_sentences=random.randint(2, 4)),
                        status=ReviewStatus.PENDIENTE,
                        user_id=user.id,
                        historic_site_id=site.id,
                        created_at=timestamp,
                        updated_at=timestamp,
                    )
                )

        if not pending_reviews:
            print("No se generaron reseñas pendientes.")
            return

        db.session.add_all(pending_reviews)
        db.session.commit()
    finally:
        enable_audit_listeners()


def seed_rejected_reviews():
    """Genera cincuenta reseñas rechazadas en sitios publicados al azar."""
    import random
    from datetime import datetime, timezone

    from faker import Faker

    from core.audit import disable_audit_listeners, enable_audit_listeners
    from core.models import Review, User
    from core.models.review import ReviewStatus
    from core.services.historic_site_service import get_published_historic_sites

    print("Generando reseñas rechazadas para sitios publicados...")

    fake = Faker("es_AR")

    sites = get_published_historic_sites()
    if not sites:
        print("No hay sitios publicados para generar reseñas rechazadas.")
        return

    public_users = User.query.join(User.role).filter_by(name="Usuario público").all()
    if not public_users:
        print("No hay usuarios públicos para generar reseñas rechazadas.")
        return

    # Generamos la mayor cantidad posible de combinaciones únicas sitio/usuario
    site_user_pairs = []
    for site in sites:
        existing_user_ids = {review.user_id for review in site.reviews}
        available_users = [
            user for user in public_users if user.id not in existing_user_ids
        ]
        site_user_pairs.extend((site, user) for user in available_users)

    if not site_user_pairs:
        print("No hay combinaciones disponibles para reseñas rechazadas.")
        return

    total_reviews = 50
    selected_pairs = random.sample(
        site_user_pairs, min(total_reviews, len(site_user_pairs))
    )

    disable_audit_listeners()

    rejected_reviews = []
    try:
        for site, user in selected_pairs:
            timestamp = fake.date_time_between(
                start_date="-1y", end_date="now", tzinfo=timezone.utc
            )
            rejected_reviews.append(
                Review(
                    rating=random.randint(1, 5),
                    content=fake.paragraph(nb_sentences=random.randint(2, 4)),
                    status=ReviewStatus.RECHAZADA,
                    user_id=user.id,
                    historic_site_id=site.id,
                    created_at=timestamp,
                    updated_at=timestamp,
                )
            )

        if not rejected_reviews:
            print("No se generaron reseñas rechazadas.")
            return

        db.session.add_all(rejected_reviews)
        db.session.commit()
    finally:
        enable_audit_listeners()
