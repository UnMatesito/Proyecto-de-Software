from core.database import db
from core.models import FeatureFlag
from datetime import datetime, timezone
# TODO: Agregar docstrings


def get_all_feature_flags():
    return FeatureFlag.query.all()


def get_feature_flag_by_id(id):
    return FeatureFlag.query.get(id)


def get_feature_flag_by_name(name):
    return FeatureFlag.query.filter(FeatureFlag.name == name).first()


def create_feature_flag(**kwargs):
    feature_flag = FeatureFlag(**kwargs)
    db.session.add(feature_flag)
    db.session.commit()
    return feature_flag


def update_feature_flag(id, **kwargs):
    feature_flag = get_feature_flag_by_id(id)
    if not feature_flag:
        return None
    for key, value in kwargs.items():
        setattr(feature_flag, key, value)
    db.session.commit()
    return feature_flag


def delete_feature_flag(id):
    feature_flag = get_feature_flag_by_id(id)
    if not feature_flag:
        return False
    db.session.delete(feature_flag)
    db.session.commit()
    return True


def toggle_feature_flag(id, is_enabled,user):
    feature_flag = get_feature_flag_by_id(id)
    if not feature_flag:
        return None
    feature_flag.is_enabled = is_enabled
    feature_flag.last_modified_by= user
    feature_flag.last_modified_at = datetime.now(timezone.utc)
    db.session.commit()
    return feature_flag


def set_maintenance_message(id, message):
    feature_flag = get_feature_flag_by_id(id)
    if not feature_flag:
        return None
    feature_flag.maintenance_message = message
    db.session.commit()
    return feature_flag


def is_feature_flag_enabled(name):
    feature_flag = get_feature_flag_by_name(name)
    if not feature_flag:
        return False
    return feature_flag.is_enabled


def get_maintenance_message(name):
    feature_flag = get_feature_flag_by_name(name)
    if not feature_flag:
        return None
    return feature_flag.maintenance_message
