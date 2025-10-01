from core.database import db
from core.models import ConservationState

# TODO: Completar y agregar dosctrings


def get_conservation_state_by_id(conservation_id):
    conservation = ConservationState.query.get(conservation_id)
    if not conservation:
        raise ValueError(
            f"No existe estado de conservacion con el id {conservation_id}"
        )
    return conservation


def get_all_conservation_state():
    return ConservationState.query.all()
