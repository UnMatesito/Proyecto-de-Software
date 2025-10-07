import re

from flask import has_request_context, session
from sqlalchemy import event, inspect

from core.database import db
from core.models.historic_site import HistoricSite
from core.services.event_type_service import get_event_type_by_name
from core.services.site_history_service import create_site_history


def get_current_user_id():
    """Obtiene el user_id desde la sesión de Flask."""
    return session.get("user_id")


@event.listens_for(HistoricSite, "after_insert")
def log_creation_history(mapper, connection, target):
    """Registra la creación de un sitio histórico."""
    user_id = get_current_user_id()
    if not user_id:
        raise ValueError("User ID no encontrado en la sesión.")

    event_type = get_event_type_by_name("Creación")
    if event_type:
        create_site_history(
            historic_site_id=target.id,
            user_id=user_id,
            event_type=event_type,
            description=f"Sitio '{target.name}' creado.",
        )


@event.listens_for(HistoricSite, "after_update")
def log_update_history(mapper, connection, target):
    """
    Registra de manera detallada los cambios realizados sobre un sitio histórico.
    Incluye ediciones, eliminaciones, restauraciones, cambio de estado y cambio de tags.
    Cada campo modificado genera un registro independiente en site_history.
    """
    user_id = get_current_user_id()
    if not user_id:
        raise ValueError("User ID no encontrado en la sesión.")

    instance_state = inspect(target)
    ignored_fields = ["updated_at", "created_at"]

    changed_attributes = [
        attr.key
        for attr in instance_state.attrs
        if attr.history.has_changes() and attr.key not in ignored_fields
    ]

    if not changed_attributes:
        return

    # Manejo de cambios en tags
    if "tags" in changed_attributes:
        tags_history = instance_state.attrs.tags.history

        old_tags = set(tags_history.deleted) if tags_history.deleted else set()
        new_tags = set(tags_history.added) if tags_history.added else set()

        added_tags = new_tags - old_tags
        removed_tags = old_tags - new_tags

        if added_tags or removed_tags:
            if added_tags:
                for tag in added_tags:
                    event_type = get_event_type_by_name("Cambio de tags")
                    description = (
                        f'Se agregó el tag "{tag.name}" al sitio "{target.name}".'
                    )
                    create_site_history(
                        historic_site_id=target.id,
                        user_id=user_id,
                        event_type=event_type,
                        description=description,
                    )

            if removed_tags:
                for tag in removed_tags:
                    event_type = get_event_type_by_name("Cambio de tags")
                    description = (
                        f'Se quitó el tag "{tag.name}" del sitio "{target.name}".'
                    )
                    create_site_history(
                        historic_site_id=target.id,
                        user_id=user_id,
                        event_type=event_type,
                        description=description,
                    )

            return  # Evita que se procese de nuevo más abajo

    # Eliminación o restauración
    if "deleted_at" in changed_attributes:
        history = instance_state.attrs.deleted_at.history
        old_value = history.deleted[0] if history.deleted else None
        new_value = history.added[0] if history.added else None

        if old_value is None and new_value is not None:
            action_type = "Eliminación"
            description = f'Sitio "{target.name}" eliminado.'
        elif old_value is not None and new_value is None:
            action_type = "Restauración"
            description = f'Sitio "{target.name}" restaurado.'
        else:
            return

        event_type = get_event_type_by_name(action_type)
        if event_type:
            create_site_history(
                historic_site_id=target.id,
                user_id=user_id,
                event_type=event_type,
                description=description,
            )
        return

    # Cambio de visibilidad
    if "is_visible" in changed_attributes and len(changed_attributes) == 1:
        action_type = "Cambio de estado"
        description = f'Visibilidad de "{target.name}" modificada.'
        event_type = get_event_type_by_name(action_type)
        if event_type:
            create_site_history(
                historic_site_id=target.id,
                user_id=user_id,
                event_type=event_type,
                description=description,
            )
        return

    # Edición general
    action_type = "Edición"

    for attr_name in changed_attributes:
        # Ignorar si ya fue procesado arriba (ej. deleted_at, is_visible, tags)
        if attr_name in ["deleted_at", "is_visible", "tags"]:
            continue

        attr = instance_state.attrs[attr_name]
        old = attr.history.deleted[0] if attr.history.deleted else None
        new = attr.history.added[0] if attr.history.added else None

        # Formatear nombre y valores
        field_label = format_field_name(attr_name)
        old_val = format_field_value(attr_name, old, instance_state)
        new_val = format_field_value(attr_name, new, instance_state)

        # Crear registro individual por campo
        description = (
            f"Se modificó el campo '{field_label}' del sitio '{target.name}': "
            f"{old_val} → {new_val}"
        )

        event_type = get_event_type_by_name(action_type)
        if event_type:
            create_site_history(
                historic_site_id=target.id,
                user_id=user_id,
                event_type=event_type,
                description=description,
            )



# Métodos para deshabilitar y habilitar eventos (necesario para poder hacer seeds)


def disable_audit_listeners():
    """Desactiva temporalmente los listeners de auditoría de HistoricSite."""
    try:
        event.remove(HistoricSite, "after_insert", log_creation_history)
    except Exception:
        pass
    try:
        event.remove(HistoricSite, "after_update", log_update_history)
    except Exception:
        pass
    print("Listeners de auditoría desactivados temporalmente.")


def enable_audit_listeners():
    """Restaura los listeners de auditoría de HistoricSite."""
    try:
        event.listen(HistoricSite, "after_insert", log_creation_history)
        event.listen(HistoricSite, "after_update", log_update_history)
        print("Listeners de auditoría restaurados.")
    except Exception as e:
        print(f"No se pudieron restaurar los listeners de auditoría: {e}")

# Métodos de utilidades
def format_field_name(field_name):
    """Convierte nombres de campos técnicos a nombres legibles en español."""
    field_names = {
        "name": "Nombre",
        "brief_description": "Descripción breve",
        "full_description": "Descripción completa",
        "inauguration_year": "Año de inauguración",
        "is_visible": "Visibilidad",
        "location": "Ubicación",
        "city_id": "Ciudad",
        "conservation_state_id": "Estado de conservación",
        "category_id": "Categoría",
    }
    return field_names.get(field_name, field_name)


def format_field_value(attr_name, value, instance_state):
    """Formatea valores de campos para mostrar de manera legible."""
    if value is None:
        return "sin valor"

    # Formatear ubicación (POINT de PostGIS)
    if attr_name == "location":
        try:
            # Extraer coordenadas del formato POINT o hexadecimal
            value_str = str(value)

            # Si es formato hexadecimal (como 0101000020e6100000...)
            if value_str.startswith("01"):
                # Intentar obtener las coordenadas del objeto
                from geoalchemy2.shape import to_shape
                point = to_shape(value)
                return f"({point.x:.6f}, {point.y:.6f})"

            # Si ya es formato POINT
            coords = re.findall(r'-?\d+\.?\d*', value_str)
            if len(coords) >= 2:
                lon, lat = coords[0], coords[1]
                return f"({lon}, {lat})"

            return value_str
        except:
            return str(value)

    # Formatear relaciones (objetos con atributo 'name')
    if hasattr(value, 'name'):
        return f'"{value.name}"'

    # Formatear booleanos
    if isinstance(value, bool):
        return "Sí" if value else "No"

    # Otros valores
    return str(value)