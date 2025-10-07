from core.services.event_type_service import get_event_type_by_name
from core.services.site_history_service import create_site_history
from flask import session, has_request_context
from sqlalchemy import event, inspect


from core.database import db
from core.models.historic_site import HistoricSite


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
    Registra la Edición, Eliminación, Restauración o el Cambio de Estado de un sitio histórico.
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

    action_type = None
    description = None

    # Manejo de cambios en tags
    if "tags" in changed_attributes:
        tags_history = instance_state.attrs.tags.history

        # Obtener tags anteriores y actuales
        old_tags = set(tags_history.deleted) if tags_history.deleted else set()
        new_tags = set(tags_history.added) if tags_history.added else set()

        added_tags = new_tags - old_tags
        removed_tags = old_tags - new_tags

        if added_tags or removed_tags:
            # Construir mensaje combinado
            description_parts = []

            if added_tags:
                tag_names = ", ".join([f'"{tag.name}"' for tag in added_tags])
                description_parts.append(
                    f"Se agregó{'aron' if len(added_tags) > 1 else ''} el{'los' if len(added_tags) > 1 else ''} tag{' s' if len(added_tags) > 1 else ''}: {tag_names}"
                )

            if removed_tags:
                tag_names = ", ".join([f'"{tag.name}"' for tag in removed_tags])
                description_parts.append(
                    f"Se quitó{'aron' if len(removed_tags) > 1 else ''} el{'los' if len(removed_tags) > 1 else ''} tag{' s' if len(removed_tags) > 1 else ''}: {tag_names}"
                )

            tags_description = (
                " y ".join(description_parts) + f' del sitio "{target.name}".'
            )

            event_type = get_event_type_by_name("Cambio de tags")
            if event_type:
                create_site_history(
                    historic_site_id=target.id,
                    user_id=user_id,
                    event_type=event_type,
                    description=tags_description,
                )

        # Remover 'tags' para evitar que se procese como una edición general
        changed_attributes.remove("tags")

        # Si no hay más cambios, retornar
        if not changed_attributes:
            return

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
    elif "is_visible" in changed_attributes:
        action_type = "Cambio de estado"
        description = f'Visibilidad de "{target.name}" modificada.'
    elif changed_attributes:
        action_type = "Edición"
        description = f'Sitio "{target.name}" modificado.'

    if action_type:
        event_type = get_event_type_by_name(action_type)
        if event_type:
            create_site_history(
                historic_site_id=target.id,
                user_id=user_id,
                event_type=event_type,
                description=description,
            )
