from core.models import EventType


def get_event_type_by_name(name: str):
    """Devuelve un EventType por nombre."""
    return EventType.query.filter_by(name=name).first()


def get_all_event_types():
    """Devuelve todos los tipos de eventos."""
    return EventType.query.all()
