import re

from flask import session
from geoalchemy2.shape import to_shape
from sqlalchemy import event, inspect

from core.models.historic_site import HistoricSite
from core.models.site_image import SiteImage
from core.services.event_type_service import get_event_type_by_name
from core.services.site_history_service import create_site_history


def get_current_user_id():
    """Obtiene el user_id desde la sesión de Flask."""
    return session.get("user_id")


def _create_history_entry(site, user_id, event_type_name, description):
    """Helper para crear entradas de historial."""
    event_type = get_event_type_by_name(event_type_name)
    if event_type:
        create_site_history(
            historic_site_id=site.id,
            user_id=user_id,
            event_type=event_type,
            description=description,
        )


@event.listens_for(HistoricSite, "after_insert")
def log_creation_history(mapper, connection, target):
    """Registra la creación de un sitio histórico."""
    user_id = get_current_user_id()
    if not user_id:
        raise ValueError("User ID no encontrado en la sesión.")

    _create_history_entry(target, user_id, "Creación", f"Sitio '{target.name}' creado.")

    # Evitar registrar cambios de campos luego de la creación, dado que el after_update se dispara
    target._skip_next_audit = True


@event.listens_for(HistoricSite, "after_update")
def log_update_history(mapper, connection, target):
    """Registra cambios detallados sobre un sitio histórico."""

    # Evitar registrar cambios inmediatamente después de la creación
    if getattr(target, "_skip_next_audit", False):
        delattr(target, "_skip_next_audit")
        return

    user_id = get_current_user_id()
    if not user_id:
        raise ValueError("User ID no encontrado en la sesión.")

    instance_state = inspect(target)
    changed_attributes = _get_changed_attributes(instance_state)

    if not changed_attributes:
        return

    # Manejo de casos especiales
    if "tags" in changed_attributes:
        _handle_tags_change(instance_state, target, user_id)
        return

    if "deleted_at" in changed_attributes:
        _handle_deletion_restoration(instance_state, target, user_id)
        return

    if (
        "pending_validation" in changed_attributes
        and "is_visible" in changed_attributes
    ):
        _handle_validation_change(instance_state, target, user_id)
        return

    if (
        "is_visible" in changed_attributes
        and "pending_validation" not in changed_attributes
    ):
        _handle_visibility_change(instance_state, target, user_id)
        return

    # Edición general
    _handle_general_edit(instance_state, target, user_id, changed_attributes)

def _get_site_from_image(target):
    """Obtiene el sitio asociado a una imagen, intentando distintos métodos."""
    site = getattr(target, "historic_site", None)
    if site:
        return site

    state = inspect(target)
    session = getattr(state, "session", None)
    if session:
        return session.get(HistoricSite, target.historic_site_id)

    try:
        return HistoricSite.query.get(target.historic_site_id)
    except Exception:
        return None


def _format_image_label(target):
    """Genera una representación legible de la imagen."""
    if target.title:
        return f'"{target.title}"'
    return f"con URL {target.public_url}"


@event.listens_for(SiteImage, "after_insert")
def log_image_added(mapper, connection, target):
    """Registra la creación de una imagen asociada a un sitio."""

    user_id = get_current_user_id()
    if not user_id:
        raise ValueError("User ID no encontrado en la sesión.")

    site = _get_site_from_image(target)
    if not site:
        return

    desc = (
        f"Se agregó la imagen {_format_image_label(target)} al sitio \"{site.name}\"."
    )
    _create_history_entry(site, user_id, "Cambio de imágenes", desc)


@event.listens_for(SiteImage, "after_update")
def log_image_updates(mapper, connection, target):
    """Registra cambios relevantes en una imagen."""

    user_id = get_current_user_id()
    if not user_id:
        raise ValueError("User ID no encontrado en la sesión.")

    site = _get_site_from_image(target)
    if not site:
        return

    state = inspect(target)
    messages = []

    if state.attrs.order.history.has_changes():
        old_order = state.attrs.order.history.deleted[0] if state.attrs.order.history.deleted else None
        new_order = state.attrs.order.history.added[0] if state.attrs.order.history.added else None
        old_text = old_order if old_order is not None else "sin orden"
        new_text = new_order if new_order is not None else "sin orden"
        messages.append(
            f"Se cambió el orden de la imagen {_format_image_label(target)} en el sitio \"{site.name}\": {old_text} → {new_text}."
        )

    if state.attrs.is_cover.history.has_changes():
        old_cover = state.attrs.is_cover.history.deleted[0] if state.attrs.is_cover.history.deleted else None
        new_cover = state.attrs.is_cover.history.added[0] if state.attrs.is_cover.history.added else None

        if new_cover is True:
            messages.append(
                f"La imagen {_format_image_label(target)} fue establecida como portada del sitio \"{site.name}\"."
            )
        elif old_cover is True and new_cover is False:
            messages.append(
                f"La imagen {_format_image_label(target)} dejó de ser la portada del sitio \"{site.name}\"."
            )

    for message in messages:
        _create_history_entry(site, user_id, "Cambio de imágenes", message)


@event.listens_for(SiteImage, "before_delete")
def log_image_removed(mapper, connection, target):
    """Registra la eliminación de una imagen."""

    user_id = get_current_user_id()
    if not user_id:
        raise ValueError("User ID no encontrado en la sesión.")

    site = _get_site_from_image(target)
    if not site:
        return

    desc = (
        f"Se eliminó la imagen {_format_image_label(target)} del sitio \"{site.name}\"."
    )
    _create_history_entry(site, user_id, "Cambio de imágenes", desc)


def _get_changed_attributes(instance_state):
    """Obtiene lista de atributos modificados, excluyendo duplicados FK/relación."""
    ignored_fields = ["updated_at", "created_at"]
    changed = [
        attr.key
        for attr in instance_state.attrs
        if attr.history.has_changes() and attr.key not in ignored_fields
    ]

    # Evitar duplicados entre relaciones y sus FK
    cleaned = []
    for attr in changed:
        if attr.endswith("_id") and attr[:-3] in changed:
            continue
        cleaned.append(attr)

    return cleaned


def _handle_tags_change(instance_state, target, user_id):
    """Maneja cambios en tags."""
    tags_history = instance_state.attrs.tags.history
    old_tags = set(tags_history.deleted or [])
    new_tags = set(tags_history.added or [])

    for tag in new_tags - old_tags:
        desc = f'Se agregó el tag "{tag.name}" al sitio "{target.name}".'
        _create_history_entry(target, user_id, "Cambio de tags", desc)

    for tag in old_tags - new_tags:
        desc = f'Se quitó el tag "{tag.name}" del sitio "{target.name}".'
        _create_history_entry(target, user_id, "Cambio de tags", desc)


def _handle_deletion_restoration(instance_state, target, user_id):
    """Maneja eliminación o restauración."""
    history = instance_state.attrs.deleted_at.history
    old_value = history.deleted[0] if history.deleted else None
    new_value = history.added[0] if history.added else None

    if old_value is None and new_value is not None:
        _create_history_entry(
            target, user_id, "Eliminación", f'Sitio "{target.name}" eliminado.'
        )
    elif old_value is not None and new_value is None:
        _create_history_entry(
            target, user_id, "Restauración", f'Sitio "{target.name}" restaurado.'
        )


def _handle_visibility_change(instance_state, target, user_id):
    """Maneja cambios de visibilidad."""
    history = instance_state.attrs.is_visible.history
    old_value = history.deleted[0] if history.deleted else None
    new_value = history.added[0] if history.added else None

    old_text = "No oculto" if old_value else "Oculto"
    new_text = "No oculto" if new_value else "Oculto"

    desc = f'Visibilidad de "{target.name}" modificada: {old_text} → {new_text}.'
    _create_history_entry(target, user_id, "Cambio de estado", desc)


def _handle_validation_change(instance_state, target, user_id):
    """Maneja cambio de validación."""
    history = instance_state.attrs.pending_validation.history
    old_val = history.deleted[0] if history.deleted else None
    new_val = history.added[0] if history.added else None

    if old_val is True and new_val is False:
        desc = f'El sitio "{target.name}" fue validado y ahora es visible al público.'
        _create_history_entry(target, user_id, "Cambio de estado", desc)


def _handle_general_edit(instance_state, target, user_id, changed_attributes):
    """Maneja ediciones generales de campos."""
    for attr_name in changed_attributes:
        if attr_name in ["deleted_at", "is_visible", "tags", "pending_validation"]:
            continue

        attr = instance_state.attrs[attr_name]
        old = attr.history.deleted[0] if attr.history.deleted else None
        new = attr.history.added[0] if attr.history.added else None

        field_label = _format_field_name(attr_name)
        old_val = _format_field_value(attr_name, old, instance_state)
        new_val = _format_field_value(attr_name, new, instance_state)

        desc = f"Se modificó el campo '{field_label}' del sitio '{target.name}': {old_val} → {new_val}"
        _create_history_entry(target, user_id, "Edición", desc)

    # Detectar cambio de provincia al cambiar ciudad
    if "city" in changed_attributes or "city_id" in changed_attributes:
        _handle_province_change(instance_state, target, user_id)


def _handle_province_change(instance_state, target, user_id):
    """Detecta y registra cambio de provincia al cambiar ciudad."""
    try:
        city_history = instance_state.attrs.city.history
        old_city = city_history.deleted[0] if city_history.deleted else None
        new_city = city_history.added[0] if city_history.added else None

        if old_city and new_city and old_city.province_id != new_city.province_id:
            old_province = (
                old_city.province.name if old_city.province else "sin provincia"
            )
            new_province = (
                new_city.province.name if new_city.province else "sin provincia"
            )

            desc = f"Se modificó el campo 'Provincia' del sitio '{target.name}': \"{old_province}\" → \"{new_province}\""
            _create_history_entry(target, user_id, "Edición", desc)
    except Exception:
        pass


# Funciones para desactivar/reactivar listeners de auditoría (necesarios para seeds)


AUDIT_LISTENERS = [
    (HistoricSite, "after_insert", log_creation_history),
    (HistoricSite, "after_update", log_update_history),
    (SiteImage, "after_insert", log_image_added),
    (SiteImage, "after_update", log_image_updates),
    (SiteImage, "before_delete", log_image_removed),
]


def disable_audit_listeners():
    """Desactiva temporalmente los listeners de auditoría."""
    for model, event_name, listener in AUDIT_LISTENERS:
        try:
            event.remove(model, event_name, listener)
        except Exception:
            pass
    print("Listeners de auditoría desactivados temporalmente.")


def enable_audit_listeners():
    """Restaura los listeners de auditoría."""
    restored_all = True
    for model, event_name, listener in AUDIT_LISTENERS:
        try:
            event.listen(model, event_name, listener)
        except Exception as e:
            restored_all = False
            print(
                f"No se pudieron restaurar los listeners de auditoría ({listener.__name__}): {e}"
            )
    if restored_all:
        print("Listeners de auditoría restaurados.")


# Métodos de utilidades para formateo
FIELD_NAMES = {
    "name": "Nombre",
    "brief_description": "Descripción breve",
    "full_description": "Descripción completa",
    "inauguration_year": "Año de inauguración",
    "is_visible": "Visibilidad",
    "location": "Ubicación",
    "city_id": "Ciudad",
    "city": "Ciudad",
    "conservation_state_id": "Estado de conservación",
    "conservation_state": "Estado de conservación",
    "category_id": "Categoría",
    "category": "Categoría",
    "tags": "Etiquetas",
}


def _format_field_name(field_name):
    """Convierte nombres de campos técnicos a nombres legibles."""
    return FIELD_NAMES.get(field_name, field_name)


def _format_field_value(attr_name, value, instance_state):
    """Formatea valores para mostrarlos de manera legible."""
    if value is None:
        return "sin valor"

    # Coordenadas (POINT de PostGIS)
    if attr_name == "location":
        value_str = str(value)
        if value_str.startswith("01"):  # formato binario WKB
            point = to_shape(value)
            return f"({point.x:.6f}, {point.y:.6f})"

        coords = re.findall(r"-?\d+\.?\d*", value_str)
        if len(coords) >= 2:
            return f"({coords[0]}, {coords[1]})"
        return value_str

    # Objetos relacionados
    display_name = _get_related_display(value)
    if display_name:
        return f'"{display_name}"'

    # Si es FK, buscar la relación
    if attr_name.endswith("_id"):
        related_obj = getattr(instance_state.object, attr_name[:-3], None)
        display_name = _get_related_display(related_obj)
        if display_name:
            return f'"{display_name}"'

    # Booleanos
    if isinstance(value, bool):
        return "Sí" if value else "No"

    return str(value)


def _get_related_display(obj):
    """Devuelve un nombre legible del objeto relacionado."""
    if not obj:
        return None
    for field in ("name", "nombre", "state", "description", "label"):
        if hasattr(obj, field):
            return getattr(obj, field)
    return None
