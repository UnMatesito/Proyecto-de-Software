from datetime import datetime, timezone

from core.database import db
from core.models import FeatureFlag


def get_all_feature_flags():
    """Retorna todo los flags"""
    return FeatureFlag.query.all()


def get_all_feature_flags_ordered_by_id():
    """Retorna todo los flags ordenados por id de forma ascendente (para mostrarlos en la vista y que no se muevan)"""
    return FeatureFlag.query.order_by(FeatureFlag.id.asc()).all()


def get_feature_flag_by_id(id):
    """Retorna un flag por id"""
    return FeatureFlag.query.get(id)


def get_feature_flag_by_name(name):
    """Retorna un flag por nombre"""
    return FeatureFlag.query.filter(FeatureFlag.name == name).first()


def create_feature_flag(**kwargs):
    """Crea un flag"""
    feature_flag = FeatureFlag(**kwargs)
    db.session.add(feature_flag)
    db.session.commit()
    return feature_flag


def update_feature_flag(id, **kwargs):
    """Actualiza un flag"""
    feature_flag = get_feature_flag_by_id(id)
    # Si no se encuentra
    if not feature_flag:
        return None
    for key, value in kwargs.items():
        setattr(feature_flag, key, value)
    db.session.commit()
    return feature_flag


def delete_feature_flag(id):
    """Elimina un flag"""
    feature_flag = get_feature_flag_by_id(id)
    if not feature_flag:
        return False
    db.session.delete(feature_flag)
    db.session.commit()
    return True


def toggle_feature_flag(id, is_enabled, user):
    """Cambia el estado de un flag y registra quien lo cambio"""
    feature_flag = get_feature_flag_by_id(id)
    # Si no se encuentra
    if not feature_flag:
        return None
    # Si es mantenimiento y esta activo, se borra el mensaje de estado, para ingresar otro al momento de activarlo nuevamente
    if feature_flag.is_maintenance():
        if feature_flag.is_enabled:
            feature_flag.maintenance_message = ""
    feature_flag.is_enabled = is_enabled
    feature_flag.last_modified_by = user
    feature_flag.last_modified_at = datetime.now(timezone.utc)
    db.session.commit()
    return feature_flag


def set_maintenance_message(id, message):
    """Setea mensaje de mantenimiento"""
    feature_flag = get_feature_flag_by_id(id)
    if not feature_flag:
        return None
    feature_flag.maintenance_message = message
    db.session.commit()
    return feature_flag


def is_feature_flag_enabled(name):
    """Retorna el estado del flag"""
    feature_flag = get_feature_flag_by_name(name)
    if not feature_flag:
        return False
    return feature_flag.is_enabled


def get_maintenance_message(name):
    """Retorna el mensaje del flag"""
    feature_flag = get_feature_flag_by_name(name)
    if not feature_flag:
        return None
    return feature_flag.maintenance_message
